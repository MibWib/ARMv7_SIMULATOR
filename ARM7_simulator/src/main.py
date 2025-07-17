
"""
-------------------------------------------------------
[program description]
-------------------------------------------------------
Author:  Kieran Mochrie
ID:      169048254
Email:   moch8254@mylaurier.ca
__updated__ = "2025-06-26"
-------------------------------------------------------
"""
# imports
# Constants
import sys
import os
from file_reader import load_binary
from memory import init_memory, read_word
from registers import init_registers, get_register, set_register, print_registers
from decoder import decode_instruction
from executor import execute_instruction
from flags import check, flag
from memory_hierarchy import init_memory_hierarchy, memory_hierarchy, read_instruction_with_cache
from decoder import decode_instruction
from executor import execute_instruction
from memory_hierarchy import read_instruction_with_cache
from registers import get_register, set_register



def get_bin_file_length(filepath):
    """Returns the length of the binary file in bytes."""
    return os.path.getsize(filepath)


def run_single_simulation(binary_file):
    """Original simulation code - runs once with default cache config"""
    init_memory()
    init_registers()
    init_memory_hierarchy()  # Initialize with default cache configuration

    if load_binary(binary_file) != 0:
        print("Failed to load binary file.")
        return 1

    filepath = binary_file
    file_length = int(get_bin_file_length(filepath))
    print("file length:", file_length)

    while get_register(15) < (file_length - 4):
        pc = get_register(15)
        instruction = read_instruction_with_cache(pc)  # Use cache for instruction fetch

        decoded = decode_instruction(instruction)
        if not decoded.is_valid:
            print(f"Halting on invalid instruction at 0x{pc:08X}")
            break

        print("decoded", decoded)

        if check(instruction, decoded):
            execute_instruction(decoded, 1 if flag['c'] else 0)

        if get_register(15) == pc:
            set_register(15, pc + 4)
            print("\nCurrent Register States:")
            print_registers()
            print("--------------------------\n")

    print("\nFinal Register States:")
    print_registers()
    
    # Print cache statistics
    if memory_hierarchy:
        memory_hierarchy.print_stats()
    
    return 0


def run_cache_experiments(binary_file):
    """Run experiments with different cache configurations"""
    
    # Different cache configurations to test
    configurations = [
        # L1 block size, L2 block size, L1 associativity
        (4, 16, 1),    # Direct mapped L1, 4B blocks
        (8, 32, 1),    # Direct mapped L1, 8B blocks
        (16, 32, 1),   # Direct mapped L1, 16B blocks
        (32, 64, 1),   # Direct mapped L1, 32B blocks
        (16, 32, 1024//16),  # Fully associative L1, 16B blocks
        (32, 64, 1024//32),  # Fully associative L1, 32B blocks
    ]
    
    results = []
    best_config = None
    best_cost = float('inf')
    
    print(f"\n{'='*60}")
    print(f"CACHE CONFIGURATION EXPERIMENTS FOR {binary_file}")
    print(f"{'='*60}")
    
    for i, (l1_block, l2_block, l1_assoc) in enumerate(configurations):
        print(f"\nConfiguration {i+1}:")
        print(f"L1: {l1_block}B blocks, {'Direct' if l1_assoc == 1 else 'Fully Associative'}")
        print(f"L2: {l2_block}B blocks, Direct mapped")

        init_memory()
        init_registers()
        global memory_hierarchy
        memory_hierarchy = init_memory_hierarchy(l1_block, l2_block, l1_assoc)
        
        if load_binary(binary_file) != 0:
            print("Failed to load binary file.")
            continue

        file_length = int(get_bin_file_length(binary_file))
        
        memory_hierarchy.reset_stats()
        
        while get_register(15) < (file_length - 4):
            pc = get_register(15)
            instruction = read_instruction_with_cache(pc)

            decoded = decode_instruction(instruction)
            if not decoded.is_valid:
                print(f"Halting on invalid instruction at 0x{pc:08X}")
                break

            if check(instruction, decoded):
                execute_instruction(decoded, 1 if flag['c'] else 0)

            if get_register(15) == pc:
                set_register(15, pc + 4)
        
        stats = memory_hierarchy.get_total_stats()
        results.append({
            'config': f"L1:{l1_block}B-{'DM' if l1_assoc == 1 else 'FA'}_L2:{l2_block}B-DM",
            'l1_block_size': l1_block,
            'l2_block_size': l2_block,
            'l1_associativity': 'Direct' if l1_assoc == 1 else 'Fully Associative',
            'l1_misses': stats['total_l1_misses'],
            'l2_misses': stats['total_l2_misses'],
            'writebacks': stats['total_writebacks'],
            'cost': stats['cost']
        })
        
        print(f"L1 Misses: {stats['total_l1_misses']}")
        print(f"L2 Misses: {stats['total_l2_misses']}")
        print(f"Writebacks: {stats['total_writebacks']}")
        print(f"Cost: {stats['cost']:.2f}")
        
        if stats['cost'] < best_cost:
            best_cost = stats['cost']
            best_config = results[-1]
    
    #saves results to file
    output_file = f"cache_results_{os.path.basename(binary_file)}.json"
    with open(output_file, 'w') as f:
        json.dump({
            'binary_file': binary_file,
            'configurations': results,
            'best_configuration': best_config
        }, f, indent=2)
    
    print(f"\n{'='*60}")
    print("BEST CONFIGURATION:")
    if best_config:
        print(f"Config: {best_config['config']}")
        print(f"Cost: {best_config['cost']:.2f}")
        print(f"L1 Misses: {best_config['l1_misses']}")
        print(f"L2 Misses: {best_config['l2_misses']}")
        print(f"Writebacks: {best_config['writebacks']}")
    
    print(f"\nResults saved to: {output_file}")
    print(f"{'='*60}")


def main():
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <binary_file> [--experiments]")
        return 1

    binary_file = sys.argv[1]
    
    if len(sys.argv) > 2 and sys.argv[2] == "--experiments":
        run_cache_experiments(binary_file)
    else:
        return run_single_simulation(binary_file)

    return 0


if __name__ == "__main__":
    sys.exit(main())
