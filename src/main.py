from solidity_address_mapper.mapper import MapperResult, Mapper

if __name__ == "__main__":
    print("Hex 1798")
    print(Mapper.map_hex_address(
        combined_json_path="../BeerBar.json",
        address_hex="1798",
        contract_name="BeerBar",
        contracts_folder="../contracts"))

    print("\nHex 90e")
    print(Mapper.map_hex_address(
        combined_json_path="../BeerBar.json",
        address_hex="90e",
        contract_name="BeerBar",
        contracts_folder="../contracts"))

    print("\nHex 0xdda")
    print(Mapper.map_hex_address(
        combined_json_path="../BeerBar.json",
        address_hex="0xdda",
        contract_name="BeerBar.sol",
        contracts_folder="../contracts"))

    print("\nHex 0x1525")
    print(Mapper.map_hex_address(
        combined_json_path="../BeerBar.json",
        address_hex="0x1525",
        contract_name="BeerBar.sol",
        contracts_folder="../contracts/"))
