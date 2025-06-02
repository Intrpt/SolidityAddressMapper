from pytest_csv_params.decorator import csv_params

import os
(DIR,FILE) = os.path.split(__file__)
(BASE,EXT) = os.path.splitext(FILE)

from solidity_address_mapper.mapper import Mapper, MapperResult


@csv_params(
    base_dir=DIR,
    data_file=f"{BASE}.csv",
    id_col="id"
)

def test_instruction_index(
        compiler_output_json: str,
        contract_node: str,
        contract_name: str
):
    """Test that the instruction index is correctly calculated."""
    # Create a mapping from 'opcode' to 'index', for each index in the bin_runtime.
    # For example, the frequent initial bytes, 0x60 and 0x80, belong to the PUSH1 instruction.
    # Verifies that the mapping is correct by comparing our instructions with the given opccodes.

    if not os.path.isfile(compiler_output_json):
        raise FileNotFoundError(f"compiler_output_json not found: {compiler_output_json}")
    bin_runtime = Mapper._read_from_json_file(
        compiler_output_json,
        f"contracts.{contract_node}.{contract_name}.evm.deployedBytecode.object")
    opcodes = Mapper._read_from_json_file(
        compiler_output_json,
        f"contracts.{contract_node}.{contract_name}.evm.deployedBytecode.opcodes")
    instruction_map = create_instruction_mapping(bin_runtime, opcodes)

    # Test the Mapper
    for idx, (start, end) in instruction_map:
        for i in range(start, end + 1):
            # For each position in bin_runtime we get the instruction index from the mapper
            # The instruction index should be equal to the idx from instruction_map.
            # For example, for the first two bytes (0,1) we should get instruction index 0 (PUSH1) and so on.
            instruction_index = Mapper._instruction_index_from_hex_address(i, bin_runtime)
            assert instruction_index == idx, f"expected {idx} but got {instruction_index}"




def create_instruction_mapping(
        bin_runtime: str,
        opcodes: str
) -> list[tuple[int, tuple[int, int]]]:
    """Maps instruction indices to byte ranges in the binary runtime."""

    # Create a mapping from 'opcode' to 'index', for each index in the bin_runtime.
    # For example, the frequent initial bytes, 0x60 and 0x80, belong to the PUSH1 instruction.
    # Verifies that the mapping is correct by comparing our instructions with the given opccodes.

    def format_push_data(data_bytes: bytes) -> str:
        """Converts data bytes to a hex string without leading zeros."""
        value = int.from_bytes(data_bytes, byteorder="big")
        hex_str = hex(value)[2:]  # Strip '0x'
        return f"0x{hex_str.upper()}" if value != 0 else "0x0"

    bytecode = bytes.fromhex(bin_runtime)
    mapping = []
    bytecode_index = 0
    instruction_idx = 0

    # opcodes counter is used to verify that we have constructed the same amount of opcodes as the compiler
    opcodes_counter = 0

    while bytecode_index < len(bytecode):
        op = bytecode[bytecode_index]

        if 0x60 <= op <= 0x7f:  # PUSH1-PUSH32
            # calculate the position (start, end) where the payload for the PUSH operation is located
            data_size = op - 0x5f
            start = bytecode_index
            end = bytecode_index + data_size  # inclusive range
            mapping.append((instruction_idx, (start, end)))

            # read the payload for the PUSH operation from the bytecode
            data_bytes = bytecode[bytecode_index + 1:bytecode_index + 1 + data_size]
            # append zero padding until its length is equal data_size
            data_bytes = data_bytes + b'\x00' * (data_size - len(data_bytes))

            formatted_data = format_push_data(data_bytes)

            bytecode_index += 1 + data_size

            # the compiler create for a PUSH3 the following entry in opcodes: PUSH3 0x362A95
            # therefore we have to add additionally 1 to the opcodes_counter (+1 for 0x362A95)
            opcodes_counter +=1
        else:
            mapping.append((instruction_idx, (bytecode_index, bytecode_index)))
            bytecode_index += 1

        instruction_idx += 1

        # we have to add additionally 1 to the opcodes_counter (+1 for the last instruction)
        opcodes_counter+=1


    # verify we got the same amount of instructions as the compiler
    assert (opcodes_counter == len(opcodes.split()))

    return mapping
