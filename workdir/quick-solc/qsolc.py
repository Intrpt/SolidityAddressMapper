import argparse
import os
import json
import subprocess

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

def main():
    parser = argparse.ArgumentParser(description="A script to process input flags.")

    parser.add_argument('-s', '--sources', required=True, nargs='+', type=str, help="Path(s) to solidity scripts you want to compile.")
    parser.add_argument('-o', '--output', type=str, help="Output file path. If not provided, the output will be printed to stdout.")
    parser.add_argument('--remappings', nargs='+', type=str, help="List of remappings. Optional.")

    parser.add_argument('--evmVersion', type=str, default="istanbul", help="Version of the EVM to compile for. Optional. Default: 'istanbul'.")
    parser.add_argument('--viaIR', type=str_to_bool, default="false", help=" Change compilation pipeline to go through the Yul intermediate representation. Optional. Default: false.")


    # optimizer flags
    parser.add_argument('--optimizer', type=str_to_bool, help="Turn on the optimizer. Optional. Default defined by solc.")
    parser.add_argument('--optimizer-runs', type=int, help="Number of optimizer runs. Optional. Default defined by solc.")
    parser.add_argument('--optimizer-details-peephole', type=str_to_bool, help="Peephole optimizer (opcode-based). Optional. Default defined by solc.")
    parser.add_argument('--optimizer-details-inliner', type=str_to_bool, help="Inliner (opcode-based). Optional. Default defined by solc.")
    parser.add_argument('--optimizer-details-jumpdest-remover', type=str_to_bool, help="Unused JUMPDEST remover (opcode-based). Optional. Default defined by solc.")
    parser.add_argument('--optimizer-details-order-literals', type=str_to_bool, help="Literal reordering (codegen-based). Optional. Default defined by solc.")
    parser.add_argument('--optimizer-details-deduplicate', type=str_to_bool, help="Block deduplicator (opcode-based). Optional. Default defined by solc.")
    parser.add_argument('--optimizer-details-cse', type=str_to_bool, help="Common subexpression elimination (opcode-based). Optional. Default defined by solc.")
    parser.add_argument('--optimizer-details-constant-optimizer', type=str_to_bool, help="Constant optimizer (opcode-based). Optional. Default defined by solc.")
    parser.add_argument('--optimizer-details-simple-counter-for-loop-unchecked-increment', type=str_to_bool, help="Unchecked loop increment (codegen-based). Optional. Default defined by solc.")
    parser.add_argument('--optimizer-details-yul', type=str_to_bool, help="Yul optimizer. Optional. Default: true when optimization is enabled. Default defined by solc.")
    parser.add_argument('--optimizer-details-yul-stack-allocation', type=str_to_bool, help="Stack allocation in Yul optimizer. Optional. Default defined by solc.")
    parser.add_argument('--optimizer-details-yul-steps', type=str, help="Optimization step sequence for Yul optimizer. Optional. Default defined by solc.")
    
    # Debugging flags are not valid for 0.5.17
    #parser.add_argument('--debug-revertStrings', type=validate_revert_strings, help="How to treat revert (and require) reason strings. Optional. Default defined by solc.")
    #parser.add_argument('--debug-debugInfo', type=str, nargs='+', help="How much extra debug information to include in comments in the produced EVM assembly and Yul code Optional. Default defined by solc.")
    parser.add_argument('--metadata-appendCBOR', type=str_to_bool, help="The CBOR metadata is appended at the end of the bytecode by default. Optional. Default defined by solc.")
    parser.add_argument('--metadata-bytecodeHash', type=str_to_bool, help="Use the given hash method for the metadata hash that is appended to the bytecode. Optional. Default defined by solc.")
    #TODO: metadata-bytecodeHash arguments


    # Parse arguments
    args = parser.parse_args()
    
    # Initialize the JSON structure
    result = {
        "language": "Solidity",
        "settings": {
            "evmVersion": args.evmVersion,
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
            #"debug": {} #Debug is not valid for 0.5.17
        },
        "sources": {}
    }

    # Add remappings if provided
    if args.remappings:
        result["settings"]["remappings"] = args.remappings

    # Add the viaIR flag
    if args.viaIR:
        result["settings"]["viaIR"] = args.viaIR
    
    # Process each file path
    for file_path in args.sources:
        # Check if the file exists
        if not os.path.isfile(file_path):
            print(f"Error: The file '{file_path}' does not exist.")
            continue
        
        # Get the relative file path
        relative_path = os.path.relpath(file_path)
        
        # Add the file to the JSON structure with the relative path in "urls"
        result["sources"][relative_path] = {
            "urls": [relative_path]
        }
    
    # Add the optimizer settings
    if args.optimizer is not None:
        result["settings"]["optimizer"]["enabled"] = args.optimizer
    if args.optimizer_runs is not None:
        result["settings"]["optimizer"]["runs"] = args.optimizer_runs
    result["settings"]["optimizer"] = {
        "details": {
            key: value for key, value in {
                "peephole": args.optimizer_details_peephole,
                "inliner": args.optimizer_details_inliner,
                "jumpdestRemover": args.optimizer_details_jumpdest_remover,
                "orderLiterals": args.optimizer_details_order_literals,
                "deduplicate": args.optimizer_details_deduplicate,
                "cse": args.optimizer_details_cse,
                "constantOptimizer": args.optimizer_details_constant_optimizer,
                "simpleCounterForLoopUncheckedIncrement": args.optimizer_details_simple_counter_for_loop_unchecked_increment,
                "yul": args.optimizer_details_yul,
                "yulDetails": {
                    "stackAllocation": args.optimizer_details_yul_stack_allocation,
                    "optimizerSteps": args.optimizer_details_yul_steps
                } if args.optimizer_details_yul is not None else None
            }.items() if value is not None 
        }
    }

    # Add the debug settings
    #if args.debug_revertStrings is not None:
    #    result["settings"]["debug"]["revertStrings"] = args.debug_revertStrings
    #if args.debug_debugInfo is not None:
    #    result["settings"]["debug"]["debugInfo"] = args.debug_debugInfo

    # Add the metadata settings
    if args.metadata_appendCBOR is not None:
        result["settings"]["metadata"]["appendCBOR"] = args.metadata_appendCBOR
    if args.metadata_bytecodeHash is not None:
        result["settings"]["metadata"]["bytecodeHash"] = args.metadata_bytecodeHash


    with open("input.json", 'w') as f:
        f.write(json.dumps(result, indent=4))

    # Check if we have to allow directories
    directories = [os.path.abspath(file_path) for file_path in args.sources]

    # Run solc
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