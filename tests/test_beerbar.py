from solidity_address_mapper.mapper import Mapper, MapperResult


class TestClass:
    def test_require(self):
        ''' Test line 54 "require(hasRole)" in the BeerBar contract '''
        result: MapperResult = Mapper.map_hex_address(
            combined_json_path="tests/compiler0826/compiled/BeerBar.json",
            address_hex="773",
            contract_name="BeerBar.sol",
            contracts_folder="tests/compiler0826")
        self._assert_code_in_line(result, 'require(hasRole(OWNER, msg.sender), "Barkeepers have to be set by owners")', 54)
    

    def test_PUSH32(self):
        ''' Test line 56 "emit BarkeeperAdded(account)" in the BeerBar contract.
         This conains a PUSH32 instruction.'''
        result: MapperResult = Mapper.map_hex_address(
            combined_json_path="tests/compiler0826/compiled/BeerBar.json",
            address_hex="79F",
            contract_name="BeerBar.sol",
            contracts_folder="tests/compiler0826")
        self._assert_code_in_line(result, 'BarkeeperAdded(account)', 56)
    
    def test_after_PUSH32(self):
        ''' Test line 56 "emit BarkeeperAdded(account)" in the BeerBar contract.
         This instruction is one after the PUSH32.'''
        result: MapperResult = Mapper.map_hex_address(
            combined_json_path="tests/compiler0826/compiled/BeerBar.json",
            address_hex="7C0",
            contract_name="BeerBar.sol",
            contracts_folder="tests/compiler0826")
        self._assert_code_in_line(result, 'BarkeeperAdded(account)', 56)



    def _assert_code_in_line(self, result: any, MapperResult: str, line: int):
        assert (result != None)
        assert (MapperResult == result.code)
        assert (result.file == "tests\\compiler0826\\Contracts\\BeerBar.sol")
        assert (result.line == line)