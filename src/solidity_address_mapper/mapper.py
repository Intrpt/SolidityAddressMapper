import os
import re
import io
from pathlib import Path

import ijson

class MapperResult:
    """
    Represents the result of a mapping operation from hex address to source code.

    This class holds information about the mapped code, including the file path,
    the specific code snippet, and the line number where it appears.

    Attributes:
        file (str): Path to the source file containing the code.
        code (str): The code snippet that was mapped to.
        line (int): Line number in the source file where the code appears.
    """

    def __init__(self, file: str | Path, code: str, line: int):
        """
        Initialize a MapperResult instance.

        Args:
            file (str): Path to the source file containing the code.
            code (str): The code snippet that was mapped to.
            line (int): Line number in the source file where the code appears.
        """
        self.file = file
        self.code = code
        self.line = line

    def __str__(self) -> str:
        """
        Returns a string representation of the MapperResult.

        Returns:
            str: A formatted string showing file path, line number, and code.
        """
        return f"{self.file}:{self.line}:{self.code}"



class Mapper:
    """
    Maps hexadecimal addresses from compiled Solidity contracts back to their source code.

    This class provides functionality to translate EVM bytecode addresses to their
    corresponding locations in Solidity source files, which is useful for debugging
    and analysis purposes.
    """
    @staticmethod
    def map_hex_address(
            compiler_output_json: str,
            address_hex: str,
            contract_name: str) \
            -> MapperResult:
        """
                Maps a hexadecimal address to its corresponding source code location.

                This method takes a hex address from compiled EVM deployed runtime bytecode and locates the
                corresponding source code in the original Solidity files. It works by analyzing
                the compiler output to find the exact instruction that corresponds to the given address.

                Args:
                    compiler_output_json (str): Path to the JSON output from the Solidity compiler.
                    address_hex (str): Hexadecimal address to map (can handle both with and without '0x' prefix).
                    contract_name (str): Name of the contract containing the address.

                Returns:
                    MapperResult: Object containing file path, code snippet, and line number.
                                  In the event of an error, the file path will be set to the contract name,
                                  the code snippet signifies the error message and the line number will be designated as 0.


                Example:
                    ```python
                    result = Mapper.map_hex_address(
                        "build/mycontract_compiled.json",
                        "0xa1b2c3",
                        "MyContract"
                    )
                    print(f"Address maps to: {result}")
                    ```
                """
        try:

            if not os.path.isfile(compiler_output_json):
                raise FileNotFoundError(f"compiler_output_json not found: {compiler_output_json}")

            address_dec = int(address_hex, 16)
            # contract node is the node representing the contract in the json file.
            contract_node = Mapper._contract_key_for_contract_name(compiler_output_json, contract_name)
            if contract_node == contract_name:
                print("WARNING: contract file name is equal to contract name, likely you have used the solidity file name as contract name.")
            meta_data_json = Mapper._read_from_json_file(compiler_output_json,f"contracts.{contract_node}.{contract_name}.metadata")

            #Verify compiler version
            compiler_version = Mapper._read_from_json_string(meta_data_json, "compiler.version")
            if compiler_version < "0.5.17":
                print(f"WARNING: The contract has been compiled using compiler version {compiler_version}. "
                      "The mapper has not been tested with this version. ")


            # Map hex address to instruction index
            bin_runtime = Mapper._read_from_json_file(compiler_output_json, f"contracts.{contract_node}.{contract_name}.evm.deployedBytecode.object")
            instruction_index = Mapper._instruction_index_from_hex_address(address_dec, bin_runtime)
            del bin_runtime # Free memory
            if instruction_index == 0:
                raise ValueError(f"Could not find instruction for index {instruction_index} in deployedBytecode.object."
                    "This may happen for an invalid hex address.")

            # Get instruction for given instruction index
            srcmap_runtime = Mapper._read_from_json_file(compiler_output_json, f"contracts.{contract_node}.{contract_name}.evm.deployedBytecode.sourceMap")
            try:
                instruction = Mapper._instruction_from_instruction_index(srcmap_runtime, instruction_index)
            except ValueError as ex:
                return MapperResult(
                    contract_node, ex.__str__(),0)

            del srcmap_runtime # Free memory
            if instruction is None:
                raise ValueError(f"Could not find instruction for index {instruction_index} in source map."
                    "This may happen for an invalid hex address.")

            if instruction['file_id'] == -1:
                raise ValueError("instruction is not associated with any particular source file. "
                    "This may happen for bytecode sections stemming from compiler-generated inline assembly statements.")

            return Mapper._source_code_from_instruction(
                compiler_output_json=compiler_output_json,
                instruction=instruction,
                meta_data_json=meta_data_json
            )
        except Exception as ex:
            return MapperResult(contract_name, ex.__str__(), 0)

    @staticmethod
    def _source_code_from_instruction(compiler_output_json:str ,instruction: dict,meta_data_json: str):
        """
        Extracts and maps a specific segment of source code based on instruction details, compiler output, and metadata.

        Parameters:
        compiler_output_json: str
            A JSON file path of the compiler's output, containing source IDs and their metadata mappings.
        instruction: dict
            A dictionary containing specific details (file_id, offset, length) to reference the required code snippet.
        meta_data_json: str
            A JSON string of metadata that includes mapping and potentially literal content of source files.

        Returns:
        str
            A specific snippet of source code according to the provided instruction in MapperResult format.

        Raises:
        ValueError
            - If the given file_id in the instruction references a compiler-internal file that cannot be mapped.
            - If the referenced source in metadata does not include actual code content.
        """
        try:
            source = next(filter(lambda x: x[1]['id'] == instruction["file_id"],
                                 Mapper._read_from_json_file(compiler_output_json, "sources").items()))
        except StopIteration:
            raise ValueError(
                f"The address references a compiler-internal file (file id: {instruction['file_id']}) and cannot be mapped to the source code.")

        source_name = source[0]
        source = next(
            filter(lambda x: x[0] == source_name, Mapper._read_from_json_string(meta_data_json, "sources").items()))
        if not 'content' in source[1]:
            raise ValueError(
                f"The metadata of source '{source_name}' doesnt include the source code. Did you set useLiteralContent true?")

        snippet = Mapper._read_snippet_from_string(
            string_content=source[1]['content'],
            start=instruction['offset'],
            length=instruction['length'])

        return MapperResult(file=source_name, code=snippet['code'], line=snippet['line'])

    @staticmethod
    def _contract_key_for_contract_name(combined_json_path: str, contract_name: str) -> str:
        """
        Finds the fully qualified contract key in the combined JSON for a given contract name.

        Args:
            combined_json_path (str): Path to the combined JSON output from the Solidity compiler.
            contract_name (str): Name of the contract to find.

        Returns:
            str: The fully qualified contract key as it appears in the combined JSON.

        Raises:
            ValueError: If multiple contracts match the name or if no contract is found.
        """
        contracts = Mapper._read_from_json_file(combined_json_path, "contracts")
        matches = Mapper._contract_name_matches(contract_name, contracts.items())
        if len(matches) > 1:
            raise ValueError(
                f"Multiple possible contracts found for name {contract_name}: {list(map(lambda x: x[0], matches))}")
        if len(matches) == 0:
            raise ValueError(f"No contract found for name {contract_name} in {combined_json_path}.")
        return matches[0][0]

    @staticmethod
    def _contract_name_matches(contract_name: str, options) -> list[tuple[str, str]]:
        """
        Filters contract options to find those matching the given contract name.

        Performs case-insensitive regex matching to find contracts whose path/name
        contains the specified contract name.

        Args:
            contract_name (str): The contract name to match.
            options: An iterable of (key, value) pairs to search through.

        Returns:
            list: A list of matching (key, value) pairs.
        """
        regex = f"(^|[\\/]){contract_name}.*"
        matches = list(filter(lambda x: re.search(regex, x[0], re.IGNORECASE) is not None, options))
        return matches

    @staticmethod
    def _read_snippet_from_string(string_content: str, start: int, length: int) -> dict[str, int | str] | None:
        """
        Reads a specific snippet from a string based on character offsets.

        Args:
            file_path (str or Path): Path to the source file to read from.
            start (int): Starting character position (0-based).
            length (int): Number of characters to read.

        Returns:
            dict: A dictionary containing:
                - 'file': The file path (str)
                - 'code': The extracted code snippet (str)
                - 'line': The line number (int)

        """

        newline_count = string_content[:start].count('\n')
        snippet = string_content[start: start + length]

        return {
            'code': snippet,
            'line': newline_count + 1,  # +1 because line numbers are 1-based
        }

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


        # If the PC is at the beginning of the bytecode, return 0 as it indicates the first instruction
        if pc == 0:
            return 0

        instruction_index: int = -1  # count how many actual EVM instructions we've seen.
        push_data_bytes = 0 # Length of the data bytes for PUSH instructions

        # Idea: Go byte by byte until we reach the given program counter (pc) or the end of the bytecode.
        # current_pc = current position (in bytes) as we walk through the bytecode
        # current_op = current opcode (in bytes) as we walk through the bytecode
        # bytecode_length_with_padding = the length of the bytecode inclusive padding zeros
        bytecode_length_with_padding = 0
        for current_pc, current_op in enumerate(bytecode_bytes):
            if push_data_bytes > 0:
                push_data_bytes -= 1
            else:
                instruction_index += 1
                bytecode_length_with_padding += 1
                if 0x60 <= current_op <= 0x7f:  # PUSH1 to PUSH32
                    push_data_bytes = current_op - 0x5f  # Calculate number of data bytes (0x60 - 0x5f = 1 (PUSH1))
                    bytecode_length_with_padding += push_data_bytes
            if current_pc == pc:
                break

        if pc > bytecode_length_with_padding:
            raise ValueError(f"PC value {pc} is greater than the length of the bytecode {bytecode_length_with_padding}")

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
            'jump': None, # type of jump (e.g., i = into function, o = out of function, - = no jump)
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

        if result['file_id'] is None:
            raise ValueError(f"Could not find file_id for instruction index {instruction_index}. There is an issue with the source map.")
        elif result['offset'] is None:
            raise ValueError(f"Could not find offset for instruction index {instruction_index}. There is an issue with the source map.")
        elif result['length'] is None:
            raise ValueError(f"Could not find length for instruction index {instruction_index}. There is an issue with the source map.")
        elif result['jump'] is None:
            # We dont need to raise an error here, because we dont need to know the jump type
            print(f"INFO: Could not find jump for instruction index {instruction_index}")
        elif result['modifiers'] is None:
            # We dont need to raise an error here, because we dont need to know the modifier depth
            print(f"INFO: Could not find modifiers for instruction index {instruction_index}")

        return {
            'offset': result['offset'],
            'length': result['length'],
            'file_id': result['file_id'],
            'jump': result['jump'],
            'modifiers': result['modifiers']
        }

    @staticmethod
    def _read_from_json_string(json_str:str, item_path: str):
        byte_stream = io.BytesIO(json_str.encode('utf-8'))
        objects = ijson.items(ijson.parse(byte_stream), item_path)
        try:
            return next(objects)
        except StopIteration:
            raise KeyError(f"Path '{item_path}' not found in JSON string '{json_str}'")

    @staticmethod
    def _read_from_json_file(file_path, item_path: str):
        """
        Reads a value from a JSON file using a dot-notation path.

        This method allows accessing nested JSON structures using a path string
        with dot notation (e.g., "contracts.MyContract.bin-runtime").

        Args:
            file_path (str): Path to the JSON file to read from.
            item_path (str): Dot-notation path to the desired value within the JSON.

        Returns:
            Any: The value at the specified path in the JSON file.

        Raises:
            FileNotFoundError: If the JSON file does not exist.
            KeyError: If the path does not exist in the JSON structure.
        """
        with open(file_path, "rb") as f:
            objects = ijson.items(f, item_path)
            try:
                return next(objects)
            except StopIteration:
                raise KeyError(f"Path '{item_path}' not found in JSON file '{file_path}'")

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Map a hex address in EVM bytecode to Solidity source code location."
    )
    parser.add_argument(
        "--compiler_output_json", "-j", required=True, help="Path to the Solidity compiler output JSON file."
    )
    parser.add_argument(
        "--address_hex", "-a", required=True, help="Hexadecimal address (e.g., 0x1525 or 1525)."
    )
    parser.add_argument(
        "--contract_name", "-c", required=True, help="Name of the contract."
    )

    args = parser.parse_args()

    result = Mapper.map_hex_address(
        compiler_output_json=args.compiler_output_json,
        address_hex=args.address_hex,
        contract_name=args.contract_name,
    )
    print(result)