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
import json
import sys
import os
import json
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
    
    # Complete configuration testing as per requirements
    l1_block_sizes = [4, 8, 16, 32]  # All required block sizes
    l2_block_sizes = [16, 32, 64]    # All required block sizes
    l1_associativities = [1, 1024//16, 1024//32]  # Direct mapped and fully associative for different block sizes
    
    configurations = []
    
    # Generate all valid combinations
    for l1_block in l1_block_sizes:
        for l2_block in l2_block_sizes:
            # Direct mapped L1
            configurations.append((l1_block, l2_block, 1))
            
            # Fully associative L1 (if block size allows)
            if l1_block <= 32:  # Reasonable constraint for fully associative
                fa_assoc = 1024 // l1_block
                configurations.append((l1_block, l2_block, fa_assoc))
    
    results = []
    best_config = None
    best_cost = float('inf')
    
    print(f"\n{'='*80}")
    print(f"CACHE CONFIGURATION EXPERIMENTS FOR {binary_file}")
    print(f"Testing {len(configurations)} different configurations")
    print(f"{'='*80}")
    
    for i, (l1_block, l2_block, l1_assoc) in enumerate(configurations):
        print(f"\nConfiguration {i+1}/{len(configurations)}:")
        print(f"L1: {l1_block}B blocks, {'Direct-mapped' if l1_assoc == 1 else f'{l1_assoc}-way associative'}")
        print(f"L2: {l2_block}B blocks, Direct-mapped")

        init_memory()
        init_registers()
        global memory_hierarchy
        memory_hierarchy = init_memory_hierarchy(l1_block, l2_block, l1_assoc)
        
        if load_binary(binary_file) != 0:
            print("Failed to load binary file.")
            continue

        file_length = int(get_bin_file_length(binary_file))
        
        memory_hierarchy.reset_stats()
        
        # Run the simulation
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
        
        # Collect statistics
        stats = memory_hierarchy.get_total_stats()
        config_name = f"L1:{l1_block}B-{'DM' if l1_assoc == 1 else f'{l1_assoc}way'}_L2:{l2_block}B-DM"
        
        results.append({
            'config_id': i+1,
            'config': config_name,
            'l1_block_size': l1_block,
            'l2_block_size': l2_block,
            'l1_associativity': 'Direct-mapped' if l1_assoc == 1 else f'{l1_assoc}-way associative',
            'l1_instruction_hits': stats['l1_instruction_cache']['hits'],
            'l1_instruction_misses': stats['l1_instruction_cache']['misses'],
            'l1_data_hits': stats['l1_data_cache']['hits'],
            'l1_data_misses': stats['l1_data_cache']['misses'],
            'l2_hits': stats['l2_cache']['hits'],
            'l2_misses': stats['l2_cache']['misses'],
            'total_l1_misses': stats['total_l1_misses'],
            'total_l2_misses': stats['total_l2_misses'],
            'writebacks': stats['total_writebacks'],
            'cost': stats['cost']
        })
        
        print(f"L1 I-Cache: {stats['l1_instruction_cache']['hits']} hits, {stats['l1_instruction_cache']['misses']} misses")
        print(f"L1 D-Cache: {stats['l1_data_cache']['hits']} hits, {stats['l1_data_cache']['misses']} misses")
        print(f"L2 Cache: {stats['l2_cache']['hits']} hits, {stats['l2_cache']['misses']} misses")
        print(f"Total L1 Misses: {stats['total_l1_misses']}")
        print(f"Total L2 Misses: {stats['total_l2_misses']}")
        print(f"Writebacks: {stats['total_writebacks']}")
        print(f"Cost: {stats['cost']:.2f}")
        
        if stats['cost'] < best_cost:
            best_cost = stats['cost']
            best_config = results[-1]
    
    # Save results to file
    output_file = f"cache_results_{os.path.basename(binary_file).replace('.bin', '')}.json"
    with open(output_file, 'w') as f:
        json.dump({
            'binary_file': binary_file,
            'total_configurations_tested': len(configurations),
            'configurations': results,
            'best_configuration': best_config,
            'cost_formula': 'Cost = 0.5 * L1_misses + L2_misses + writebacks'
        }, f, indent=2)
    
    print(f"\n{'='*80}")
    print("EXPERIMENT SUMMARY:")
    print(f"Tested {len(configurations)} configurations")
    print(f"\nBEST CONFIGURATION:")
    if best_config:
        print(f"Config: {best_config['config']}")
        print(f"L1 Block Size: {best_config['l1_block_size']}B")
        print(f"L2 Block Size: {best_config['l2_block_size']}B")
        print(f"L1 Associativity: {best_config['l1_associativity']}")
        print(f"Cost: {best_config['cost']:.2f}")
        print(f"L1 Misses: {best_config['total_l1_misses']}")
        print(f"L2 Misses: {best_config['total_l2_misses']}")
        print(f"Writebacks: {best_config['writebacks']}")
    
    print(f"\nDetailed results saved to: {output_file}")
    print(f"{'='*80}")


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
