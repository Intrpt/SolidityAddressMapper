# Quick solc
The qsolc.py Python script creates a standard-JSON compiler input based on the provided input flags (see `python qsolc.py --help`). Then, it runs solc on the created compiler input. You can save the output to a file by using the `--output` flag. If no output flag is given, the result will be printed to the standard output. You can observe the generated compiler_input.json by setting the `--debug` flag. It will generate a compiler_input.json.

You provide compiler input flags as key-value parameters. Use "\\." to escape "." (dot). For instance the following key-value pair is used to define the source contract: `sources.example/BeerBar\.sol.urls[0]='example/BeerBar.sol'`.
Which will be translated to:
```json
{
    "sources": {
        "example/BeerBar.sol": {
            "urls": ["example/BeerBar.sol"]
        }
    }
}
```
Follow this scheme to set any arbritrary parameter for the compiler input. Refer to the solidity documentation for further information about [Input Description](https://docs.soliditylang.org/en/latest/using-the-compiler.html#input-description).

Note: This implementation of qsolc is slightly modified. It already sets the required input variables to create a valid output.json needed to run the solidity_address_mapper, such as useLiteralContent and outputSelection. You can find the original qsolc here: [Intrpt/quick-solc](https://github.com/Intrpt/quick-solc)

## Complete Example
After you installed the library contracts for the example BeerBar.sol using `npm i @openzeppelin/contracts` <ins>in the example folder</ins>, you can run qsolc.py from the "workdir/quick-solc" folder as follows:

```bash 
python .\qsolc.py 
settings.remappings[0]='./=example/' 
settings.remappings[1]='@openzeppelin/=example/node_modules/@openzeppelin/'  
sources.example/BeerBar\.sol.urls[0]='example/BeerBar.sol'
```


Note: The name of the contract source will be changed from "Beerbar.sol" to "example/Beerbar.sol." If you don't want this, you have to move qsolc.py into the "example" folder and run it like this:
```bash 
python .\qsolc.py 
settings.remappings[0]='@openzeppelin/=node_modules/@openzeppelin/' 
sources.BeerBar\.sol.urls[0]='BeerBar.sol'
```
Refer to the solidity documentation for further information about [Base Path and Import Remapping](https://docs.soliditylang.org/en/latest/using-the-compiler.html#base-path-and-import-remapping).