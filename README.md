Use specific solidity compiler version
```
solc-select use 0.8.9 --always-install
```


Install dependencies:
```bash
npm install @openzeppelin/contracts@4.9.6               
```

Compile:
```bash 
solc --combined-json bin,bin-runtime,srcmap,srcmap-runtime,asm,ast --base-path . --include-path ./node_modules/ .\Contracts\Agency.sol > output.json
```

For compiler 0.4.26:
```bash
solc --combined-json bin,bin-runtime,srcmap,srcmap-runtime,asm,ast --allow-paths ./node_modules/ ./Contracts/Government.sol > output.json
```