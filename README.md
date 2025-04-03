### Use specific solidity compiler version

Assuming you have installed solc-select
```
solc-select use 0.8.9 --always-install
```

### Install dependencies:

Install the libraries used by the Mapper

```bash
pip install -r requirements.txt
```

Install libraries/contracts/dependencies that are used by the contract you want to compile.
In the example of BeerBar we need @openzeppelin/contracts Version 4.9.6.
```bash
npm install @openzeppelin/contracts@4.9.6  
```

### Compile

#### Solidity compiler >= 0.6

Use the following command to create the json file:
```bash 
solc --combined-json bin-runtime,srcmap-runtime,ast --base-path . --include-path ./node_modules/ .\Contracts\BeerBar.sol > BeerBar.json
```

--base-path is the folder containing your solidity source file<br>
--include-path is the folder containing the installed npm packages

#### Solidity compiler < 0.6:
```bash
solc --combined-json bin-runtime,srcmap-runtime,ast --allow-paths ./node_modules/ ./Contracts/BeerBar.sol > BeerBar.json
```

### Using the mapper

For now you can run the mapper using ``Mapper.map_hex_address(...)`` as follows:

```python
Mapper.map_hex_address(
    combined_json_path="../BeerBar.json",
    address_hex="0x1525",
    contract_name="BeerBar.sol",
    contracts_folder="../contracts/"
)
```

combined_json_path is the json generated from the solidity compiler<br>
address_hex is the address you want to map<br>
contract_name is the contract you have compiled<br>
contracts_folder is the folder containing your contracts source files.

The result is of class ``MapperResult`` containing `line`, `code` and `file`.
If no source file has been found in the contracts_folder, then line is set to 0 and the code has been reconstructed.

