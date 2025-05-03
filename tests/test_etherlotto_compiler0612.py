from solidity_address_mapper.mapper import Mapper, MapperResult


class TestClass:
    def test_exception_state(self):
        ''' ==== Exception State ====
            SWC ID: 110
            Severity: Medium
            Contract: MAIN
            Function name: play()
            PC address: 625
            Estimated Gas Usage: 154 - 249
            An assertion violation was triggered.
            It is possible to trigger an assertion violation. Note that Solidity assert() statements should only be used to check invariants. Review the transaction trace generated for this issue and either make sure your program logic is correct, or use require() instead of assert() if your goal is to constrain user inputs or enforce preconditions. Remember to validate inputs from both callers (for instance, via passed arguments) and callees (for instance, via return values).
        '''
        result: MapperResult = Mapper.map_hex_address(
            compiler_output_json="tests/compiler0612/compiled/EtherLotto.json",
            # Decimal 625 to hex is 271. Das würde theoretisch passen weil es assert ist
            # Hex 625 to decimal is 1573 which is an invalid pc?
            address_hex="271",
            contract_name="EtherLotto",)
        self._assert_code_in_line(result, 'assert(msg.value == TICKET_AMOUNT)', 38)

    # Der Test gibt den ganzen sourcecode zurück.
    # Vielleicht weil es keine fallback function gibt?
    #def test_requirement_violation(self):
    #    ''' ==== requirement violation ====
    #    SWC ID: 123
    #    Severity: Medium
    #    Contract: MAIN
    #    Function name: fallback
    #    PC address: 189
    #    Estimated Gas Usage: 130 - 700
    #    A requirement was violated in a nested call and the call was reverted as a result.
    #    Make sure valid inputs are provided to the nested call (for instance, via passed arguments).
    #    '''
    #    result: MapperResult = Mapper.map_hex_address(
    #        compiler_output_json="tests/compiler0612/compiled/EtherLotto.json",
    #        address_hex=hex(189),
    #        contract_name="EtherLotto",)
    #    self._assert_code_in_line(result, '', 38)

    def test_dependence_on_predictable_environment_variable(self):
        ''' ==== Dependence on predictable environment variable ====
            SWC ID: 116
            Severity: Low
            Contract: MAIN
            Function name: play()
            PC address: 707
            Estimated Gas Usage: 6176 - 26835
            A control flow decision is made based on The block.timestamp environment variable.
            The block.timestamp environment variable is used to determine a control flow decision. Note that the values of variables like coinbase, gaslimit, block number and timestamp are predictable and can be manipulated by a malicious miner. Also keep in mind that attackers know hashes of earlier blocks. Don't use any of those environment variables as sources of randomness and be aware that use of these variables introduces a certain level of trust into miners.
        '''
        result: MapperResult = Mapper.map_hex_address(
            compiler_output_json="tests/compiler0612/compiled/EtherLotto.json",
            address_hex=hex(707),
            contract_name="EtherLotto",)
        self._assert_code_in_line(result, 'if (random == 0) {\n\n            // Send fee to bank account.\n            bank.transfer(FEE_AMOUNT);\n\n            // Send jackpot to winner.\n            msg.sender.transfer(pot - FEE_AMOUNT);\n\n            // Restart jackpot.\n            pot = 0;\n        }', 48)
    
    def test_multiple_calls_in_a_single_transaction(self):
        ''' ==== Multiple Calls in a Single Transaction ====
            SWC ID: 113
            Severity: Low
            Contract: MAIN
            Function name: play()
            PC address: 863
            Estimated Gas Usage: 14458 - 123819
            Multiple calls are executed in the same transaction.
            This call is executed following another call within the same transaction. It is possible that the call never gets executed if a prior call fails permanently. This might be caused intentionally by a malicious callee. If possible, refactor the code such that each transaction only executes one external call or make sure that all callees can be trusted (i.e. they’re part of your own codebase).
        '''
        result: MapperResult = Mapper.map_hex_address(
            compiler_output_json="tests/compiler0612/compiled/EtherLotto.json",
            address_hex=hex(863),
            contract_name="EtherLotto",)
        self._assert_code_in_line(result, 'msg.sender.transfer(pot - FEE_AMOUNT)', 54)





    


    def _assert_code_in_line(self, result: any, MapperResult: str, line: int):
        assert (result != None)
        assert (MapperResult == result.code)
        assert (result.file == "compiler0612/contracts/EtherLotto.sol")
        assert (result.line == line)