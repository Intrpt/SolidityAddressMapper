from pytest_csv_params.decorator import csv_params

import os
(DIR,FILE) = os.path.split(__file__)
(BASE,EXT) = os.path.splitext(FILE)

import json

from solidity_address_mapper.mapper import Mapper, MapperResult

opcode_map = {
        # Stop and Arithmetic Operations
        0x00: "STOP",
        0x01: "ADD",
        0x02: "MUL",
        0x03: "SUB",
        0x04: "DIV",
        0x05: "SDIV",
        0x06: "MOD",
        0x07: "SMOD",
        0x08: "ADDMOD",
        0x09: "MULMOD",
        0x0a: "EXP",
        0x0b: "SIGNEXTEND",

        # Comparison & Bitwise Logic
        0x10: "LT",
        0x11: "GT",
        0x12: "SLT",
        0x13: "SGT",
        0x14: "EQ",
        0x15: "ISZERO",
        0x16: "AND",
        0x17: "OR",
        0x18: "XOR",
        0x19: "NOT",
        0x1a: "BYTE",
        0x1b: "SHL",
        0x1c: "SHR",
        0x1d: "SAR",

        # SHA3
        0x20: "SHA3",

        # Environmental Information
        0x30: "ADDRESS",
        0x31: "BALANCE",
        0x32: "ORIGIN",
        0x33: "CALLER",
        0x34: "CALLVALUE",
        0x35: "CALLDATALOAD",
        0x36: "CALLDATASIZE",
        0x37: "CALLDATACOPY",
        0x38: "CODESIZE",
        0x39: "CODECOPY",
        0x3a: "GASPRICE",
        0x3b: "EXTCODESIZE",
        0x3c: "EXTCODECOPY",
        0x3d: "RETURNDATASIZE",
        0x3e: "RETURNDATACOPY",
        0x3f: "EXTCODEHASH",

        # Block Information
        0x40: "BLOCKHASH",
        0x41: "COINBASE",
        0x42: "TIMESTAMP",
        0x43: "NUMBER",
        0x44: "DIFFICULTY",
        0x45: "GASLIMIT",
        0x46: "CHAINID",
        0x47: "SELFBALANCE",
        0x48: "BASEFEE",

        # Stack, Memory, Storage and Flow Operations
        0x50: "POP",
        0x51: "MLOAD",
        0x52: "MSTORE",
        0x53: "MSTORE8",
        0x54: "SLOAD",
        0x55: "SSTORE",
        0x56: "JUMP",
        0x57: "JUMPI",
        0x58: "PC",
        0x59: "MSIZE",
        0x5a: "GAS",
        0x5b: "JUMPDEST",
        0x5c: "TLOAD",
        0x5d: "TSTORE",
        0x5e: "MCOPY",

        # Push Operations
        0x5f: "PUSH0",
        0x60: "PUSH1",
        0x61: "PUSH2",
        # ... up to PUSH32 (0x7f)
        **{i: f"PUSH{i - 0x5f}" for i in range(0x62, 0x80)},

        # Duplication Operations
        0x80: "DUP1",
        0x81: "DUP2",
        # ... up to DUP16 (0x8f)
        **{i: f"DUP{i - 0x7f}" for i in range(0x81, 0x90)},

        # Exchange Operations
        0x90: "SWAP1",
        0x91: "SWAP2",
        # ... up to SWAP16 (0x9f)
        **{i: f"SWAP{i - 0x8f}" for i in range(0x91, 0xa0)},

        # Logging
        0xa0: "LOG0",
        0xa1: "LOG1",
        0xa2: "LOG2",
        0xa3: "LOG3",
        0xa4: "LOG4",

        # System Operations
        0xf0: "CREATE",
        0xf1: "CALL",
        0xf2: "CALLCODE",
        0xf3: "RETURN",
        0xf4: "DELEGATECALL",
        0xf5: "CREATE2",
        0xfa: "STATICCALL",
        0xfd: "REVERT",
        0xfe: "INVALID",
        0xff: "SELFDESTRUCT"
    }



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
    # i.e. the first two bytes 0x60 and 0x80 belong to the PUSH1 instruction.
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
            # The instruction index should be equal to the idx from instruction_map
            # i.e. for the first two bytes (0,1) we should get instruction index 0 (PUSH1) and so on.
            instruction_index = Mapper._instruction_index_from_hex_address(i, bin_runtime)
            assert instruction_index == idx, f"expected {idx} but got {instruction_index}"




def create_instruction_mapping(
        bin_runtime: str,
        opcodes: str
) -> list[tuple[int, tuple[int, int]]]:
    """Maps instruction indices to byte ranges in the binary runtime."""

    # Create a mapping from 'opcode' to 'index', for each index in the bin_runtime.
    # i.e. the first two bytes 0x60 and 0x80 belong to the PUSH1 instruction.
    # Verifies that the mapping is correct by comparing our instructions with the given opccodes.

    def format_push_data(data_bytes: bytes) -> str:
        """Converts data bytes to a hex string without leading zeros."""
        value = int.from_bytes(data_bytes, byteorder="big")
        hex_str = hex(value)[2:]  # Strip '0x'
        return f"0x{hex_str.upper()}" if value != 0 else "0x0"

    bytecode = bytes.fromhex(bin_runtime)
    mapping = []
    i = 0
    instruction_idx = 0
    instructions = ""

    while i < len(bytecode):
        op = bytecode[i]

        if 0x60 <= op <= 0x7f:  # PUSH1-PUSH32
            data_size = op - 0x5f
            start = i
            end = i + data_size  # inclusive range
            mapping.append((instruction_idx, (start, end)))

            data_bytes = bytecode[i + 1:i + 1 + data_size]
            formatted_data = format_push_data(data_bytes)
            instructions += f"{opcode_map[op]} {formatted_data} "

            i += 1 + data_size
        else:
            mapping.append((instruction_idx, (i, i)))
            instructions += f"{opcode_map.get(op, f'DATA (0x{op:02x})')} "
            i += 1

        instruction_idx += 1

    # Verify we got the correct instructions
    assert (instructions == opcodes)

    return mapping
