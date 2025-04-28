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

class TestClass:
    bin_runtime = "608060405234801561000f575f80fd5b5060043610610029575f3560e01c80630c3b0cc41461002d575b5f80fd5b610047600480360381019061004291906100fe565b610060565b604051610057949392919061014b565b60405180910390f35b5f805f805f858761007191906101bb565b90505f868861008091906101ee565b90505f878961008f9190610221565b90505f80890361009f575f6100ac565b888a6100ab919061028f565b5b90508383838397509750975097505050505092959194509250565b5f80fd5b5f819050919050565b6100dd816100cb565b81146100e7575f80fd5b50565b5f813590506100f8816100d4565b92915050565b5f8060408385031215610114576101136100c7565b5b5f610121858286016100ea565b9250506020610132858286016100ea565b9150509250929050565b610145816100cb565b82525050565b5f60808201905061015e5f83018761013c565b61016b602083018661013c565b610178604083018561013c565b610185606083018461013c565b95945050505050565b7f4e487b71000000000000000000000000000000000000000000000000000000005f52601160045260245ffd5b5f6101c5826100cb565b91506101d0836100cb565b92508282019050808211156101e8576101e761018e565b5b92915050565b5f6101f8826100cb565b9150610203836100cb565b925082820390508181111561021b5761021a61018e565b5b92915050565b5f61022b826100cb565b9150610236836100cb565b9250828202610244816100cb565b9150828204841483151761025b5761025a61018e565b5b5092915050565b7f4e487b71000000000000000000000000000000000000000000000000000000005f52601260045260245ffd5b5f610299826100cb565b91506102a4836100cb565b9250826102b4576102b3610262565b5b82820490509291505056fea164736f6c634300081a000a"
    opcodes = "PUSH1 0x80 PUSH1 0x40 MSTORE CALLVALUE DUP1 ISZERO PUSH2 0xF JUMPI PUSH0 DUP1 REVERT JUMPDEST POP PUSH1 0x4 CALLDATASIZE LT PUSH2 0x29 JUMPI PUSH0 CALLDATALOAD PUSH1 0xE0 SHR DUP1 PUSH4 0xC3B0CC4 EQ PUSH2 0x2D JUMPI JUMPDEST PUSH0 DUP1 REVERT JUMPDEST PUSH2 0x47 PUSH1 0x4 DUP1 CALLDATASIZE SUB DUP2 ADD SWAP1 PUSH2 0x42 SWAP2 SWAP1 PUSH2 0xFE JUMP JUMPDEST PUSH2 0x60 JUMP JUMPDEST PUSH1 0x40 MLOAD PUSH2 0x57 SWAP5 SWAP4 SWAP3 SWAP2 SWAP1 PUSH2 0x14B JUMP JUMPDEST PUSH1 0x40 MLOAD DUP1 SWAP2 SUB SWAP1 RETURN JUMPDEST PUSH0 DUP1 PUSH0 DUP1 PUSH0 DUP6 DUP8 PUSH2 0x71 SWAP2 SWAP1 PUSH2 0x1BB JUMP JUMPDEST SWAP1 POP PUSH0 DUP7 DUP9 PUSH2 0x80 SWAP2 SWAP1 PUSH2 0x1EE JUMP JUMPDEST SWAP1 POP PUSH0 DUP8 DUP10 PUSH2 0x8F SWAP2 SWAP1 PUSH2 0x221 JUMP JUMPDEST SWAP1 POP PUSH0 DUP1 DUP10 SUB PUSH2 0x9F JUMPI PUSH0 PUSH2 0xAC JUMP JUMPDEST DUP9 DUP11 PUSH2 0xAB SWAP2 SWAP1 PUSH2 0x28F JUMP JUMPDEST JUMPDEST SWAP1 POP DUP4 DUP4 DUP4 DUP4 SWAP8 POP SWAP8 POP SWAP8 POP SWAP8 POP POP POP POP POP SWAP3 SWAP6 SWAP2 SWAP5 POP SWAP3 POP JUMP JUMPDEST PUSH0 DUP1 REVERT JUMPDEST PUSH0 DUP2 SWAP1 POP SWAP2 SWAP1 POP JUMP JUMPDEST PUSH2 0xDD DUP2 PUSH2 0xCB JUMP JUMPDEST DUP2 EQ PUSH2 0xE7 JUMPI PUSH0 DUP1 REVERT JUMPDEST POP JUMP JUMPDEST PUSH0 DUP2 CALLDATALOAD SWAP1 POP PUSH2 0xF8 DUP2 PUSH2 0xD4 JUMP JUMPDEST SWAP3 SWAP2 POP POP JUMP JUMPDEST PUSH0 DUP1 PUSH1 0x40 DUP4 DUP6 SUB SLT ISZERO PUSH2 0x114 JUMPI PUSH2 0x113 PUSH2 0xC7 JUMP JUMPDEST JUMPDEST PUSH0 PUSH2 0x121 DUP6 DUP3 DUP7 ADD PUSH2 0xEA JUMP JUMPDEST SWAP3 POP POP PUSH1 0x20 PUSH2 0x132 DUP6 DUP3 DUP7 ADD PUSH2 0xEA JUMP JUMPDEST SWAP2 POP POP SWAP3 POP SWAP3 SWAP1 POP JUMP JUMPDEST PUSH2 0x145 DUP2 PUSH2 0xCB JUMP JUMPDEST DUP3 MSTORE POP POP JUMP JUMPDEST PUSH0 PUSH1 0x80 DUP3 ADD SWAP1 POP PUSH2 0x15E PUSH0 DUP4 ADD DUP8 PUSH2 0x13C JUMP JUMPDEST PUSH2 0x16B PUSH1 0x20 DUP4 ADD DUP7 PUSH2 0x13C JUMP JUMPDEST PUSH2 0x178 PUSH1 0x40 DUP4 ADD DUP6 PUSH2 0x13C JUMP JUMPDEST PUSH2 0x185 PUSH1 0x60 DUP4 ADD DUP5 PUSH2 0x13C JUMP JUMPDEST SWAP6 SWAP5 POP POP POP POP POP JUMP JUMPDEST PUSH32 0x4E487B7100000000000000000000000000000000000000000000000000000000 PUSH0 MSTORE PUSH1 0x11 PUSH1 0x4 MSTORE PUSH1 0x24 PUSH0 REVERT JUMPDEST PUSH0 PUSH2 0x1C5 DUP3 PUSH2 0xCB JUMP JUMPDEST SWAP2 POP PUSH2 0x1D0 DUP4 PUSH2 0xCB JUMP JUMPDEST SWAP3 POP DUP3 DUP3 ADD SWAP1 POP DUP1 DUP3 GT ISZERO PUSH2 0x1E8 JUMPI PUSH2 0x1E7 PUSH2 0x18E JUMP JUMPDEST JUMPDEST SWAP3 SWAP2 POP POP JUMP JUMPDEST PUSH0 PUSH2 0x1F8 DUP3 PUSH2 0xCB JUMP JUMPDEST SWAP2 POP PUSH2 0x203 DUP4 PUSH2 0xCB JUMP JUMPDEST SWAP3 POP DUP3 DUP3 SUB SWAP1 POP DUP2 DUP2 GT ISZERO PUSH2 0x21B JUMPI PUSH2 0x21A PUSH2 0x18E JUMP JUMPDEST JUMPDEST SWAP3 SWAP2 POP POP JUMP JUMPDEST PUSH0 PUSH2 0x22B DUP3 PUSH2 0xCB JUMP JUMPDEST SWAP2 POP PUSH2 0x236 DUP4 PUSH2 0xCB JUMP JUMPDEST SWAP3 POP DUP3 DUP3 MUL PUSH2 0x244 DUP2 PUSH2 0xCB JUMP JUMPDEST SWAP2 POP DUP3 DUP3 DIV DUP5 EQ DUP4 ISZERO OR PUSH2 0x25B JUMPI PUSH2 0x25A PUSH2 0x18E JUMP JUMPDEST JUMPDEST POP SWAP3 SWAP2 POP POP JUMP JUMPDEST PUSH32 0x4E487B7100000000000000000000000000000000000000000000000000000000 PUSH0 MSTORE PUSH1 0x12 PUSH1 0x4 MSTORE PUSH1 0x24 PUSH0 REVERT JUMPDEST PUSH0 PUSH2 0x299 DUP3 PUSH2 0xCB JUMP JUMPDEST SWAP2 POP PUSH2 0x2A4 DUP4 PUSH2 0xCB JUMP JUMPDEST SWAP3 POP DUP3 PUSH2 0x2B4 JUMPI PUSH2 0x2B3 PUSH2 0x262 JUMP JUMPDEST JUMPDEST DUP3 DUP3 DIV SWAP1 POP SWAP3 SWAP2 POP POP JUMP INVALID LOG1 PUSH5 0x736F6C6343 STOP ADDMOD BYTE STOP EXP "
    srcmap = "25:326:0:-:0;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;65:283;;;;;;;;;;;;;:::i;:::-;;:::i;:::-;;;;;;;;;;:::i;:::-;;;;;;;;;133:7;142;151;160;180:11;198:1;194;:5;;;;:::i;:::-;180:19;;210:11;228:1;224;:5;;;;:::i;:::-;210:19;;240:11;258:1;254;:5;;;;:::i;:::-;240:19;;270:11;289:1;284;:6;:18;;301:1;284:18;;;297:1;293;:5;;;;:::i;:::-;284:18;270:32;;321:3;326;331;336;313:27;;;;;;;;;;;;65:283;;;;;;;:::o;88:117:1:-;197:1;194;187:12;334:77;371:7;400:5;389:16;;334:77;;;:::o;417:122::-;490:24;508:5;490:24;:::i;:::-;483:5;480:35;470:63;;529:1;526;519:12;470:63;417:122;:::o;545:139::-;591:5;629:6;616:20;607:29;;645:33;672:5;645:33;:::i;:::-;545:139;;;;:::o;690:474::-;758:6;766;815:2;803:9;794:7;790:23;786:32;783:119;;;821:79;;:::i;:::-;783:119;941:1;966:53;1011:7;1002:6;991:9;987:22;966:53;:::i;:::-;956:63;;912:117;1068:2;1094:53;1139:7;1130:6;1119:9;1115:22;1094:53;:::i;:::-;1084:63;;1039:118;690:474;;;;;:::o;1170:118::-;1257:24;1275:5;1257:24;:::i;:::-;1252:3;1245:37;1170:118;;:::o;1294:553::-;1471:4;1509:3;1498:9;1494:19;1486:27;;1523:71;1591:1;1580:9;1576:17;1567:6;1523:71;:::i;:::-;1604:72;1672:2;1661:9;1657:18;1648:6;1604:72;:::i;:::-;1686;1754:2;1743:9;1739:18;1730:6;1686:72;:::i;:::-;1768;1836:2;1825:9;1821:18;1812:6;1768:72;:::i;:::-;1294:553;;;;;;;:::o;1853:180::-;1901:77;1898:1;1891:88;1998:4;1995:1;1988:15;2022:4;2019:1;2012:15;2039:191;2079:3;2098:20;2116:1;2098:20;:::i;:::-;2093:25;;2132:20;2150:1;2132:20;:::i;:::-;2127:25;;2175:1;2172;2168:9;2161:16;;2196:3;2193:1;2190:10;2187:36;;;2203:18;;:::i;:::-;2187:36;2039:191;;;;:::o;2236:194::-;2276:4;2296:20;2314:1;2296:20;:::i;:::-;2291:25;;2330:20;2348:1;2330:20;:::i;:::-;2325:25;;2374:1;2371;2367:9;2359:17;;2398:1;2392:4;2389:11;2386:37;;;2403:18;;:::i;:::-;2386:37;2236:194;;;;:::o;2436:410::-;2476:7;2499:20;2517:1;2499:20;:::i;:::-;2494:25;;2533:20;2551:1;2533:20;:::i;:::-;2528:25;;2588:1;2585;2581:9;2610:30;2628:11;2610:30;:::i;:::-;2599:41;;2789:1;2780:7;2776:15;2773:1;2770:22;2750:1;2743:9;2723:83;2700:139;;2819:18;;:::i;:::-;2700:139;2484:362;2436:410;;;;:::o;2852:180::-;2900:77;2897:1;2890:88;2997:4;2994:1;2987:15;3021:4;3018:1;3011:15;3038:185;3078:1;3095:20;3113:1;3095:20;:::i;:::-;3090:25;;3129:20;3147:1;3129:20;:::i;:::-;3124:25;;3168:1;3158:35;;3173:18;;:::i;:::-;3158:35;3215:1;3212;3208:9;3203:14;;3038:185;;;;:::o"

    def test_instruction_index(self):
        """Test that the instruction index is correctly calculated."""
        # Create a mapping from 'opcode' to 'index', for each index in the bin_runtime.
        # i.e. the first two bytes 0x60 and 0x80 belong to the PUSH1 instruction.
        # Verifies that the mapping is correct by comparing our instructions with the given opccodes.
        instruction_map = self.create_instruction_mapping(self.bin_runtime, self.opcodes)

        # Test the Mapper
        for idx, (start, end) in instruction_map:
            for i in range(start, end + 1):
                # For each position in bin_runtime we get the instruction index from the mapper
                # The instruction index should be equal to the idx from instruction_map
                # i.e. for the first two bytes (0,1) we should get instruction index 0 (PUSH1) and so on.
                instruction_index = Mapper._instruction_index_from_hex_address(i, self.bin_runtime)
                assert instruction_index == idx, f"expected {idx} but got {instruction_index}"

    def test_last_instruction_before_return(self):
        ''' Test last instruction before the return statement "div = b != 0 ? a / b : 0" in the ArtithmeticTestContract contract '''
        result: MapperResult = Mapper.map_hex_address(
            combined_json_path="tests/compiler0826/compiled/ArtithmeticTestContract.json",
            address_hex=hex(174),
            contract_name="ArtithmeticTestContract.sol",
            contracts_folder="tests/compiler0826")
        self._assert_code_in_line(result, 'uint256 div = b != 0 ? a / b : 0', 7)




    def create_instruction_mapping(self, bin_runtime_hex: str, opcodes: str) -> list[tuple[int, tuple[int, int]]]:
        """Maps instruction indices to byte ranges in the binary runtime."""

        # Create a mapping from 'opcode' to 'index', for each index in the bin_runtime.
        # i.e. the first two bytes 0x60 and 0x80 belong to the PUSH1 instruction.
        # Verifies that the mapping is correct by comparing our instructions with the given opccodes.

        def format_push_data(data_bytes: bytes) -> str:
            """Converts data bytes to a hex string without leading zeros."""
            value = int.from_bytes(data_bytes, byteorder="big")
            hex_str = hex(value)[2:]  # Strip '0x'
            return f"0x{hex_str.upper()}" if value != 0 else "0x0"

        bytecode = bytes.fromhex(bin_runtime_hex)
        mapping = []
        i = 0
        instruction_idx = 0
        instructions = ""
        bin_runtime_bytes = bytes.fromhex(self.bin_runtime)

        while i < len(bytecode):
            op = bytecode[i]

            if 0x60 <= op <= 0x7f:  # PUSH1-PUSH32
                data_size = op - 0x5f
                start = i
                end = i + data_size  # inclusive range
                mapping.append((instruction_idx, (start, end)))

                data_bytes = bin_runtime_bytes[i + 1:i + 1 + data_size]
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
   


    def _assert_code_in_line(self, result: any, MapperResult: str, line: int):
        assert (result != None)
        assert (MapperResult == result.code)
        assert (result.file == "tests\\compiler0826\\Contracts\\ArtithmeticTestContract.sol")
        assert (result.line == line)