import os
import re
from pathlib import Path

import ijson
from charset_normalizer import from_path


class MapperResult:
    def __init__(self, file: str, code: str, line: int):
        self.file = file
        self.code = code
        self.line = line

    def __str__(self) -> str:
        return f"{self.file}:{self.line}:{self.code}"


class Mapper:

    @staticmethod
    def _read_compiler_version(combined_json_path: str) -> str:
        e = Mapper._read_from_json_file(combined_json_path, "")
        if "version" not in e:
            return "0.0.0"
        return e["version"]

    @staticmethod
    def map_hex_address(
            combined_json_path: str,
            address_hex: str,
            contract_name: str,
            contracts_folder: str = None) \
            -> MapperResult:

        if Mapper._read_compiler_version(combined_json_path) < "0.6.0":
            print(f"WARNING: Unsupported Compiler Version {Mapper._read_compiler_version(combined_json_path)}. "
                  "Please use a version >= 0.6.0")

        address_int = int(address_hex, 16)
        # contract_file_name = Mapper._contract_for_contract_name(combined_json_path, contract_name)
        contracts_key = Mapper._contract_for_contract_name(combined_json_path, contract_name)
        sources_key = Mapper._source_for_contract_name(combined_json_path, contract_name)

        # Map hex address to instruction index
        bin_runtime = Mapper._read_from_json_file(combined_json_path, f"contracts.{contracts_key}.bin-runtime")
        instruction_index = Mapper._instruction_index_from_hex_address(address_int, bin_runtime)
        del bin_runtime # Free memory
        if instruction_index == 0:
            raise ValueError(f"Could not find hex address {address_hex} in binary runtime")

        # Get instruction for given instruction index
        srcmap_runtime = Mapper._read_from_json_file(combined_json_path, f"contracts.{contracts_key}.srcmap-runtime")
        instruction = Mapper._instruction_from_instruction_index(srcmap_runtime, instruction_index)
        del srcmap_runtime # Free memory
        if instruction is None:
            raise ValueError(f"Could not find instruction for index {instruction_index} in source map")

        # Get Function details for the instruction
        ast_json = Mapper._read_from_json_file(combined_json_path, f"sources.{sources_key}.AST")
        function_node = Mapper._ast_node_from_instruction(ast_json, instruction)

        #If we have the source file we can directly read the instruction
        if contracts_folder:
            snippet = Mapper._read_snippet_from_source_code(function_node, combined_json_path, contracts_folder)
            return MapperResult(snippet['file'], snippet['code'], snippet['line'])
        else:
            _, _, file_id = Mapper._parse_function_node(function_node)
            file_node = Mapper._file_node_by_index(combined_json_path, int(file_id))
            return MapperResult(
                file=Mapper._file_location_from_file_node(file_node),
                code=Mapper._reconstruct_code_from_ast(function_node['expression']),
                line=0  # Set to 0. We don't have the source code so we cannot calculate the line
            )

    @staticmethod
    def _contract_for_contract_name(combined_json_path: str, contract_name: str) -> str:
        contracts = Mapper._read_from_json_file(combined_json_path, "contracts")
        matches = Mapper._contract_name_matches(contract_name, contracts.items())
        if len(matches) > 1:
            raise ValueError(
                f"Multiple possible contracts found for name {contract_name}: {list(map(lambda x: x[0], matches))}")
        if len(matches) == 0:
            raise ValueError(f"No contract found for name {contract_name} in {combined_json_path}.")
        return matches[0][0]

    @staticmethod
    def _source_for_contract_name(combined_json_path: str, contract_name: str) -> str:
        sources = Mapper._read_from_json_file(combined_json_path, "sources")
        matches = Mapper._contract_name_matches(contract_name, sources.items())
        if len(matches) > 1:
            raise ValueError(
                f"Multiple possible sources found for name {contract_name}: {list(map(lambda x: x[0], matches))}")
        if len(matches) == 0:
            raise ValueError(f"No contract found for name {contract_name} in {combined_json_path})")
        return matches[0][0]

    @staticmethod
    def _contract_name_matches(contract_name: str, options):
        regex = f"(^|[\\/]){contract_name}.*"
        matches = list(filter(lambda x: re.search(regex, x[0], re.IGNORECASE) is not None, options))
        return matches

    @staticmethod
    def _construct_contract_path(file_location: str) -> str:
        dir_path = Path(os.path.dirname(__file__))
        file_location_path = Path(file_location)
        full_path = str(dir_path / ".." / file_location_path)
        return full_path

    @staticmethod
    def _file_node_by_index(json_file_path: str, file_id: int):
        # Get the file (location) for the given file_id
        return list(Mapper._read_from_json_file(json_file_path, "sources").items())[file_id]

    @staticmethod
    def _file_location_from_file_node(file_node: dict):
        file_location = file_node[1]["AST"]["absolutePath"]
        if file_location is None:
            raise ValueError("No absolutePath in given json file.")
        return file_location

    @staticmethod
    def _parse_function_node(function_node: dict):
        src = function_node['src']

        if not src:
            print("Error: Could not calculate line. No src attribute for given function node.")
            return 0

        parts = src.split(':')
        if len(parts) != 3:
            print(
                "Error: Could not calculate line. Invalid src attribute for given function node. Expected format: offset:length:file_id")
            return 0

        return parts

    @staticmethod
    def _read_snippet_from_file(file_path: str | Path, start: int, length: int) -> dict[str, int | str] | None:
        if not os.path.isfile(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        characters_count = 0
        line_count = 0
        encoding = from_path(file_path).best().encoding
        with open(file_path, "r", encoding=encoding) as file:
            for line in file:
                characters_count += len(line)
                line_count += 1
                if characters_count >= start:
                    characters_count -= len(line)
                    start = start - characters_count
                    return {
                        'file': str(file_path),
                        'code': str(line[start:(start + int(length))]),
                        'line': int(line_count),
                    }

    @staticmethod
    def _read_snippet_from_source_code(function_node: dict, json_file_path: str, source_files_path: str) -> dict:
        # Read the source to get the position of the statement described in the function node
        start, length, file_id = Mapper._parse_function_node(function_node)
        file_node = Mapper._file_node_by_index(json_file_path, int(file_id))

        # Get the file (location) for the given file_id
        file_location = Mapper._file_location_from_file_node(file_node)
        source_file = Mapper._merge_paths(source_files_path, file_location)

        return Mapper._read_snippet_from_file(source_file, int(start), int(length))

    @staticmethod
    def _merge_paths(path1: str | Path, path2: str | Path) -> Path:
        p1_parts = Path(path1).parts
        p2_parts = Path(path2).parts

        # Find the overlap point
        for i in range(len(p1_parts)):
            if str(p1_parts[i:]).lower() == str(p2_parts[:len(p1_parts[i:])]).lower():
                merged = Path(*p1_parts[:i], *p2_parts)
                return merged

        # If no overlap, just join normally
        return Path(path1) / Path(path2)

    @staticmethod
    def _get_line_number(function_node: dict, json_file_path: str) -> int:
        # Read the source to get the position of the statement described in the function node
        src = function_node['src']

        if not src:
            print("Error: Could not calculate line. No src attribute for given function node.")
            return 0

        parts = src.split(':')
        if len(parts) != 3:
            print("Error: Could not calculate line. Invalid src attribute for given function node. Expected format: offset:length:file_id")
            return 0

        start, length, file_id = parts

        # Get the file (location) for the given file_id
        files_node = list(Mapper._read_from_json_file(json_file_path, "sources").items())[int(file_id)]
        file_location = files_node[1]["AST"]["absolutePath"]
        if file_location is None:
            print("Error: Could not calculate line. No absolutePath for given file.")
            return 0
        full_path = Mapper._construct_contract_path(file_location)

        if not os.path.isfile(full_path):
            print(f"Error: Could not calculate line. File not found: {full_path}")
            return 0

        characters_count: int = 0
        line_count: int = 0
        encoding: str = from_path(full_path).best().encoding
        with open(full_path, "r", encoding=encoding) as file:
            for line in file:
                characters_count += len(line)
                line_count += 1
                if characters_count >= int(start):
                    return line_count

        raise ValueError(f"Could not find character position {start} in file {full_path}: EOF")

    @staticmethod
    def _reconstruct_code_from_ast(node: dict) -> str:
        """
        Reconstructs Solidity source code from an AST node without access to the original source.

        This function generates a code representation based solely on the AST structure.
        The reconstruction may not match the original formatting but will be functionally
        equivalent.

        Args:
            node (dict): The AST node to reconstruct code from.

        Returns:
            str: The reconstructed Solidity code fragment.

        Raises:
            ValueError: If the node type is unsupported or required information is missing.
        """
        from solidity_ast_printer import SolidityASTPrinter
        printer = SolidityASTPrinter()
        return printer.reconstruct(node)

    @staticmethod
    def _ast_node_from_instruction(ast_json, source_location):
        """
        Finds the smallest AST node that fully contains the given source location.

        This function traverses the Solidity AST (Abstract Syntax Tree) to locate the node
        whose source range fully contains the given instruction source location, and whose
        source range is the smallest among all such matches (i.e., the most specific node).

        This is useful for mapping EVM instructions (via source maps) back to the most
        relevant Solidity source construct, such as a statement or expression.

        Args:
            ast_json (dict): The Solidity AST as a nested dictionary, typically obtained
                             from the Solidity compiler's JSON output.
            source_location (dict): A dictionary with the source mapping information for
                                    the instruction. Expected keys:
                - 'offset' (int): Starting character offset in the source file.
                - 'length' (int): Length of the source range in characters.
                - 'file_id' (int): ID of the source file (used for multi-file inputs).

        Returns:
            dict: The AST node (as a dictionary) that fully contains the given source location
                  and has the smallest source range.

        Raises:
            ValueError: If no matching AST node is found that contains the provided source location.

        Example:
            source_location = {'offset': 120, 'length': 8, 'file_id': 0}
            node = Mapper._ast_node_from_instruction(ast_json, source_location)
            print(node['nodeType'])  # e.g., 'ExpressionStatement'
        """
        target_offset = source_location['offset']
        target_length = source_location['length']
        target_file_id = source_location['file_id']
        target_end = target_offset + max(target_length, 1)

        # Track the smallest containing node
        best_match = None
        smallest_range = float('inf')  # Initialize with infinity

        # Function to recursively search through AST nodes
        def search_node(node):
            nonlocal best_match, smallest_range

            # Check if this node has source location
            if 'src' in node:
                src_parts = node['src'].split(':')
                node_offset = int(src_parts[0])
                node_length = int(src_parts[1])
                node_file_id = int(src_parts[2])
                node_end = node_offset + node_length

                # Check if this node contains our target location
                contains_target = (
                        node_file_id == target_file_id and
                        node_offset <= target_offset and
                        node_end >= target_end
                )

                # If it contains the target and has a smaller range than our current best match
                if contains_target and node_length < smallest_range:
                    best_match = node
                    smallest_range = node_length

            # Always continue searching children, even if we found a match
            for key, value in node.items():
                if isinstance(value, dict):
                    search_node(value)
                elif isinstance(value, list):
                    for item in value:
                        if isinstance(item, dict):
                            search_node(item)

        # Start search from the root
        search_node(ast_json)

        if best_match is None:
            raise ValueError(f"Could not find node for instruction at offset {target_offset} in AST")

        return best_match

    @staticmethod
    def _instruction_index_from_hex_address(pc: int, bytecode: str) -> int:
        """
        Convert a program counter (PC) value to an instruction index in the bytecode.

        This function walks through the bytecode instruction by instruction, counting valid EVM opcodes
        (including accounting for PUSHn instructions and their data), until it reaches the given PC value.

        Note:
        - If the PC points to the middle of a PUSH instruction's data, the function returns the beginning of the PUSH instruction.
        - If the PC is equal to the bytecode length, the function returns the total number of instructions.

        Args:
            pc (int): The program counter value (byte offset into the bytecode)
            bytecode (str): The contract bytecode as a hex string (without '0x' prefix)

        Returns:
            int: The corresponding instruction index
        Raises:
            ValueError: If PC is negative, bytecode is empty or invalid, or PC is beyond the bytecode length
        """
        if pc < 0:
            raise ValueError("PC value must be a positive integer")
        if bytecode is None or bytecode == "":
            raise ValueError("Bytecode cannot be empty")

        try:
            if bytecode.startswith("0x"):
                bytecode = bytecode[2:]
            bytecode_bytes = bytes.fromhex(bytecode)
        except ValueError:
            raise ValueError("Bytecode must be a valid hex string with an even number of characters")

        instruction_index: int = 0 # count how many actual EVM instructions we've seen.
        current_pc = 0 # current position (in bytes) as we walk through the bytecode

        if pc > len(bytecode_bytes):
            raise ValueError(f"PC value {pc} is greater than the length of the bytecode {len(bytecode_bytes)}")

        # Go byte by byte until we reach the given program counter (pc) or the end of the bytecode.
        while current_pc < len(bytecode_bytes) and current_pc < pc:
            opcode = bytecode_bytes[current_pc]

            # Handle PUSH instructions which have additional data bytes
            # The number after "PUSH" indicates how many bytes of data to push. For example:
            # 0x60 (PUSH1): Pushes 1 byte of data. 0x61 (PUSH2): Pushes 2 bytes of data. and so on...
            if 0x60 <= opcode <= 0x7f:  # PUSH1 to PUSH32
                data_size = opcode - 0x5f  # Calculate number of data bytes (0x60 - 0x5f = 1 (PUSH1))
                next_pc = current_pc + 1 + data_size
            # For all other instructions we read 1 byte
            else:
                next_pc = current_pc + 1

            if pc < next_pc:
                # PC is in the middle of the PUSH instruction, so stop
                break

            current_pc = next_pc
            instruction_index += 1

        return instruction_index

    @staticmethod
    def _instruction_from_instruction_index(srcmap, instruction_index):
        """
        Extracts the source code location metadata for a specific instruction index
        from a Solidity source map.

        Solidity source maps are generated by the Solidity compiler to map EVM bytecode
        instructions back to the corresponding locations in the original Solidity source code.
        Each entry in the source map may omit fields to save space, inheriting values from
        previous entries (compression).

        This function walks backward from the given instruction index to resolve all fields
        (offset, length, file ID, jump type, and modifier depth) by applying the compression rules.

        Args:
            srcmap (str): The Solidity source map string, consisting of semicolon-separated entries.
            instruction_index (int): The index of the instruction in the bytecode whose source
                                     location is to be retrieved.

        Returns:
            dict: A dictionary containing the fully resolved source mapping information with keys:
                  - 'offset' (int): Character offset in the source file.
                  - 'length' (int): Length of the code segment in characters.
                  - 'file_id' (int): Index of the source file.
                  - 'jump' (str): Type of jump ('i' = into function, 'o' = out of function, '-1' = none).
                  - 'modifiers' (int): Modifier depth at this instruction.

        Raises:
            ValueError: If the instruction index is out of bounds or the source map entry could not
                        be fully resolved due to missing fields.
        """
        # Split the source map into entries
        entries = srcmap.split(';')

        # Check if the instruction index is valid
        if instruction_index >= len(entries):
            raise ValueError(f"Invalid instruction index {instruction_index}. "
                             f"Source map contains {len(entries)} entries.")

        result = {
            'offset': None, # starting character offset in the source file
            'length': None, # number of characters this instruction corresponds to
            'file_id': None, # index of the source file
            'jump': None, # type of jump (e.g., i = into function, o = out of function, -1 = no jump)
            'modifiers': None # how deep into modifier context the instruction is
        }

        # Keep track of which fields are still missing (so we know when we are done)
        remaining = set(result.keys())

        # Iterate backwards from instruction_index and populate the values
        for i in range(instruction_index, -1, -1):
            entry = entries[i]
            if not entry:
                # Compression rule: If an entry is empty, it inherits the values from the previous entry.
                # Skip empty entries
                continue

            #offset:length:fileIndex:jump:modifierDepth
            parts = entry.split(':')

            # Update values based on this entry
            # Compression rule: If an entry omits an empty field (e.g. ''), it inherits the value from the previous entry.
            if 'offset' in remaining and len(parts) > 0 and parts[0] != '':
                result['offset'] = int(parts[0])
                remaining.remove('offset')

            if 'length' in remaining and len(parts) > 1 and parts[1] != '':
                result['length'] = int(parts[1])
                remaining.remove('length')

            if 'file_id' in remaining and len(parts) > 2 and parts[2] != '':
                result['file_id'] = int(parts[2])
                remaining.remove('file_id')

            if 'jump' in remaining and len(parts) > 3 and parts[3] != '':
                result['jump'] = parts[3]
                remaining.remove('jump')

            if 'modifiers' in remaining and len(parts) > 4 and parts[4] != '':
                result['modifiers'] = int(parts[4])
                remaining.remove('modifiers')

            if not remaining:
                break  # All fields are populated


        if any(value is None for value in result.values()):
            raise ValueError(f"Incomplete source map entry at index {instruction_index}")

        return {
            'offset': result['offset'],
            'length': result['length'],
            'file_id': result['file_id'],
            'jump': result['jump'],
            'modifiers': result['modifiers']
        }

    @staticmethod
    def _read_from_json_file(file_path, item_path: str):
        with open(file_path, "rb") as f:
            objects = ijson.items(f, item_path)
            return next(objects)


if __name__ == "__main__":
    print("Hex 0x1798")
    print(Mapper.map_hex_address(
        combined_json_path="../BeerBar.json",
        address_hex="0x1798",
        contract_name="BeerBar",
        contracts_folder="../contracts"))

    print("\nHex 0x90e")
    print(Mapper.map_hex_address(
        combined_json_path="../BeerBar.json",
        address_hex="0x90e",
        contract_name="BeerBar",
        contracts_folder="../contracts"))

    print("\nHex 0xdda")
    print(Mapper.map_hex_address(
        combined_json_path="../BeerBar.json",
        address_hex="0xdda",
        contract_name="BeerBar.sol",
        contracts_folder="../contracts"))

    print("\nHex 0x1525")
    print(Mapper.map_hex_address(
        combined_json_path="../BeerBar.json",
        address_hex="0x1525",
        contract_name="BeerBar.sol",
        contracts_folder="../contracts"))
