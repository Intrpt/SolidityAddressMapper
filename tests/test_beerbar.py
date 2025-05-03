from solidity_address_mapper.mapper import Mapper, MapperResult


class TestClass:
    def test_require(self):
        ''' Test line 54 "require(hasRole)" in the BeerBar contract '''
        result: MapperResult = Mapper.map_hex_address(
            compiler_output_json="tests/compiler0826/compiled/BeerBar.json",
            address_hex="18AB",
            contract_name="BeerBar",)
        self._assert_code_in_line(result, 'hasRole(OWNER, msg.sender)', 54)
    

    def test_PUSH32(self):
        ''' Test line 56 "emit BarkeeperAdded(account)" in the BeerBar contract.
         This conains a PUSH32 instruction.'''
        result: MapperResult = Mapper.map_hex_address(
            compiler_output_json="tests/compiler0826/compiled/BeerBar.json",
            address_hex="193F",
            contract_name="BeerBar")
        self._assert_code_in_line(result, 'BarkeeperAdded(account)', 56)
    
    def test_after_PUSH32(self):
        ''' Test line 56 "emit BarkeeperAdded(account)" in the BeerBar contract.
         This instruction is one after the PUSH32.'''
        result: MapperResult = Mapper.map_hex_address(
            compiler_output_json="tests/compiler0826/compiled/BeerBar.json",
            address_hex="1940",
            contract_name="BeerBar")
        self._assert_code_in_line(result, 'BarkeeperAdded(account)', 56)



    def _assert_code_in_line(self, result: any, MapperResult: str, line: int):
        assert (result != None)
        assert (MapperResult == result.code)
        assert (result.file == "contracts/BeerBar.sol")
        assert (result.line == line)