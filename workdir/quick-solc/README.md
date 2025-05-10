# Quick solc
The qsolc.py Python script creates a standard-JSON compiler input based on the provided input flags (see `python qsolc.py --help`). Then, it runs solc on the created compiler input. You can save the output to a file by using the `--output` flag. If no output flag is given, the result will be printed to the standard output.

## Example
After you installed the library contracts for the example BeerBar.sol using `npm i @openzeppelin/contracts` <ins>in the example folder</ins>, you can run qsolc.py from the "workdir/quick-solc" folder as follows:
```bash 
python .\qsolc.py -s example/BeerBar.sol --remappings "./=/example/" "@openzeppelin/=example/node_modules/@openzeppelin/"
```

Note: The name of the contract source will be changed from "Beerbar.sol" to "example/Beerbar.sol." If you don't want this, you have to move qsolc.py into the "example" folder and run it like this:
```bash
python .\qsolc.py -s example/BeerBar.sol --remappings "@openzeppelin/=node_modules/@openzeppelin/" -o output.json
output.json
```
Refer to the solidity documentation for further information about [Base Path and Import Remapping](https://docs.soliditylang.org/en/latest/using-the-compiler.html#base-path-and-import-remapping).