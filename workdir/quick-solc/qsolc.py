import argparse
import os
import json
import pathlib
import re
import subprocess
from typing import Dict, Any, List, Tuple

def str_to_bool(value):
    if value.lower() in {'true', '1', 'yes'}:
        return True
    elif value.lower() in {'false', '0', 'no'}:
        return False
    else:
        raise argparse.ArgumentTypeError(f"Invalid boolean value: {value}")
    
def validate_revert_strings(value):
    if value.lower() in {'default', 'strip', 'debug', 'verboseDebug'}:
        return value
    else:
        raise argparse.ArgumentTypeError(f"Invalid debug revertStrings value: {value}")
    
def update_nested_dict(d: Dict[str, Any], keys: List[str], value: Any, append_to_arrays: bool = False) -> Dict[str, Any]:
    """
    Update a nested dictionary with a value at the specified key path.
    If append_to_arrays is True, append to existing arrays instead of overwriting them.
    Returns a new dictionary with the updated structure.
    """
    if not keys:
        if append_to_arrays and isinstance(d, list) and isinstance(value, list):
            # Append to the existing array
            d.extend(value)
            return d
        return value

    current_key = keys[0]
    
    # Handle array indexing (e.g., key[0], key[1])
    if current_key.endswith(']'):
        base_key, index_str = current_key[:-1].split('[')
        try:
            index = int(index_str)
        except ValueError:
            raise ValueError(f"Invalid array index in key path: '{current_key}'.")
        
        if base_key not in d:
            d[base_key] = []
        elif not isinstance(d[base_key], list):
            raise ValueError(f"Cannot index '{base_key}' as an array; it is not a list.")
        
        # Ensure the array is long enough
        while len(d[base_key]) <= index:
            d[base_key].append(None)
        
        if len(keys) == 1:
            d[base_key][index] = value
        else:
            d[base_key][index] = update_nested_dict(
                d[base_key][index] or {}, keys[1:], value, append_to_arrays
            )
        return d

    # Handle regular dictionary keys
    if len(keys) == 1:
        if append_to_arrays and isinstance(d.get(current_key), list) and isinstance(value, list):
            d[current_key].extend(value)
        else:
            d[current_key] = value
    else:
        if current_key not in d:
            d[current_key] = {}
        elif not isinstance(d[current_key], dict):
            raise ValueError(f"Cannot set nested key '{keys[1]}' under '{current_key}'; it is not a dictionary.")
        d[current_key] = update_nested_dict(d[current_key], keys[1:], value, append_to_arrays)
    return d

def parse_key_value_pair(arg: str) -> Tuple[List[str], Any]:
    """Parse a single argument in the format 'key.path=value' into a key path and value."""
    if '=' not in arg:
        raise ValueError(f"Invalid argument format: '{arg}'. Expected 'key.path=value'.")
    
    key_path, value_str = arg.split('=', 1)  # Split on the first '=' only
    if not key_path:
        raise ValueError(f"Key path cannot be empty in argument: '{arg}'.")
    
    # Escape dots
    key_path = key_path.replace('\\.', '__TEMP_DOT_E6C8ED1B-BA4A-43DB-A8DA-742800F8E099___')

    keys = key_path.split('.')
    try:
        # Attempt to parse the value as JSON to support arrays, numbers, booleans, etc.
        value = json.loads(value_str)
    except json.JSONDecodeError:
        # If parsing fails, treat the value as a string
        value = value_str

    # Restore escaped dots
    keys = [key.replace('__TEMP_DOT_E6C8ED1B-BA4A-43DB-A8DA-742800F8E099___', '.') for key in keys]
    return keys, value

def main():
    parser = argparse.ArgumentParser(description="A script to process input flags.")
    parser.add_argument("pairs", nargs='+', help="Key-value pairs in the format 'key.path=value'")

    parser.add_argument('-o', '--output', type=str, help="Output file path. If not provided, the output will be printed to stdout.")
   
    
    # Initialize the JSON structure
    result = {
        "language": "Solidity",
        "settings": {
            "metadata": {
                "useLiteralContent": True
            },
            "outputSelection": {
                "*": {
                    "*": [
                        "evm.deployedBytecode.sourceMap",
                        "evm.deployedBytecode.object",
                        "evm.deployedBytecode.opcodes",
                        "metadata"
                    ]
                }
            },
            "optimizer": {},
            "debug": {}
        },
        "sources": {}
    }

    # Parse arguments
    args = parser.parse_args()

   # Parse json key-value pairs
    try:
        #print(f"Creating compiler input JSON....")
        for pair in args.pairs:
            keys, value = parse_key_value_pair(pair)
            result = update_nested_dict(result, keys, value)
    except ValueError as e:
        print(f"Error: {e}")

    # Save to file
    with open("input.json", 'w') as f:
        f.write(json.dumps(result, indent=4))
    #print(f"Compiler input JSON saved to input.json")

    # Check if we have to allow directories
    source_paths = []
    if 'sources' not in result or not isinstance(result['sources'], dict):
        print("Error: no 'sources' provided")
        return
    for source in result['sources'].values():
        if 'urls' in source and isinstance(source['urls'], list):
            for url in source['urls']:
                if os.path.exists(url):
                    if os.path.isdir(url):
                        source_paths.append(os.path.abspath(url))
                    elif os.path.isfile(url):
                        source_paths.append(os.path.abspath(os.path.dirname(url)))

    directories = [os.path.abspath(path) for path in source_paths]

    # Run solidity compiler
    #print("Running solidity compiler...")
    process = subprocess.Popen(
        ['solc', '--allow-paths', ','.join(directories) , '--standard-json'],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    stdout, stderr = process.communicate(input=json.dumps(result, indent=4).encode("utf-8"))

    # Return the output
    if process.returncode != 0:
        print(f"Error: {stderr.decode()}")
        return
    elif args.output:
        with open(args.output, 'w') as f:
            f.write(stdout.decode())
        print(args.output)
    else:
        print(stdout.decode())
        


if __name__ == "__main__":
    main()