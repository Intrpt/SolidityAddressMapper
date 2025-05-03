from pytest_csv_params.decorator import csv_params

import os
(DIR,FILE) = os.path.split(__file__)
(BASE,EXT) = os.path.splitext(FILE)

from solidity_address_mapper.mapper import Mapper, MapperResult

@csv_params(
    base_dir=DIR,
    data_file=f"{BASE}.csv",
    id_col="id"
)

def test_mapper(compiler_output_json, address_hex, contract_name, filename, source_code, source_line, info):
    result: MapperResult = Mapper.map_hex_address(
        compiler_output_json,
        address_hex,
        contract_name)
    assert (result != None)
    assert (result.file == filename)
    assert (result.code == source_code.replace("\\r","\r").replace("\\n","\n"))
    assert (result.line == int(source_line))
