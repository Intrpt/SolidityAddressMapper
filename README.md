# Solidity binary address to source code mapper
Use this mapper to get the line number and code snippet of a solidity source code for a given binary address (program counter).

## Constraints
* Requires python 3
* Supports solidity compiter output > 0.6
* Requires specific sections in the compiler generated output, see [Using the Mapper].

## Install dependencies:

Install the libraries used by the Mapper

```bash
pip install -r requirements.txt
```

Install libraries/contracts/dependencies that are used by the contract you want to compile.
In the example of BeerBar we need @openzeppelin/contracts Version 4.9.6.
```bash
npm install @openzeppelin/contracts@4.9.6  
```

## Using the mapper

For now you can run the mapper using ``Mapper.map_hex_address(...)`` as follows:

```python
Mapper.map_hex_address(
    compiler_output_json="../BeerBar.json",
    address_hex="0x1525",
    contract_name="BeerBar.sol",
)
```

compiler_output_json is the json generated from the solidity compiler<br>
address_hex is the address you want to map<br>
contract_name is the contract you have compiled<br>

compiler_output_json must be in standard-json format (not combined-json!) with the following output sections:
* evm.deployedBytecode.sourceMap
* evm.deployedBytecode.object
* sources 

additonally `useLiteralContent` in `metadata` should be set to true.

The result is of class ``MapperResult`` containing `line`, `code` and `file`.
If no source file has been found in the contracts_folder, then line is set to 0 and the code has been reconstructed.



