Tests for the solidity compiler version 0.8.26.
The contracts have been compiled using the following command in the project root folder:
```bash 
solc --combined-json bin-runtime,srcmap-runtime,ast --evm-version cancun --metadata-hash none --base-path . --include-path ./node_modules/ .tests\compiler0826\contracts\ArtithmeticTestContract.sol > tests\compiler0826\compiled\ArtithmeticTestContract.json
```
An equivalent sourcemap/binary can be generated using the provided `compiler_config.json`
