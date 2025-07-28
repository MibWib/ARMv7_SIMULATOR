"""
-------------------------------------------------------
Fixed ARM Simulator with Cache Hierarchy
-------------------------------------------------------
Author:  Kieran Mochrie
ID:      169048254
Email:   moch8254@mylaurier.ca
__updated__ = "2025-07-27"
-------------------------------------------------------
"""
import sys
import os
import json
from file_reader import load_binary
from memory import init_memory, read_word
from registers import init_registers, get_register, set_register, print_registers
from decoder import decode_instruction
from executor import execute_instruction
from flags import check, flag
from memory_hierarchy import init_memory_hierarchy, read_instruction_with_cache


def get_bin_file_length(filepath):
    """Returns the length of the binary file in bytes."""
    return os.path.getsize(filepath)


def run_single_simulation(binary_file):
    """Run simulation with default cache configuration"""
    print(f"Running single simulation with {binary_file}")
    
    # Initialize components
    init_memory()
    init_registers()
    
    if not init_memory_hierarchy():  # Use default configuration
        print("Failed to initialize memory hierarchy")
        return 1

    if load_binary(binary_file) != 0:
        print("Failed to load binary file.")
        return 1

    file_length = get_bin_file_length(binary_file)
    print(f"File length: {file_length} bytes")
    
    instruction_count = 0
    max_instructions = 1000  # Safety limit to prevent infinite loops

    while get_register(15) < file_length and instruction_count < max_instructions:
        pc = get_register(15)
        
        try:
            # Fetch instruction through cache
            instruction = read_instruction_with_cache(pc)
            
            # Decode instruction
            decoded = decode_instruction(instruction)
            if not decoded.is_valid:
                print(f"Invalid instruction at PC=0x{pc:08X}: 0x{instruction:08X}")
                break

            print(f"\nPC=0x{pc:08X}: {decoded.mnemonic}")
            
            # Check condition and execute
            if check(instruction, decoded):
                execute_instruction(decoded, 1 if flag['c'] else 0)
            
            # Update PC if not modified by instruction
            if get_register(15) == pc:
                set_register(15, pc + 4)
            
            instruction_count += 1
            
        except Exception as e:
            print(f"Error executing instruction at PC=0x{pc:08X}: {str(e)}")
            break

    print(f"\nSimulation completed after {instruction_count} instructions")
    print("\nFinal Register States:")
    print_registers()
    
    # Print cache statistics
    from memory_hierarchy import memory_hierarchy
    if memory_hierarchy:
        memory_hierarchy.print_stats()
    
    return 0


def run_cache_experiments(binary_file):
    """Run experiments with different cache configurations"""
    
    # Configuration parameters
    l1_block_sizes = [4, 8, 16, 32]
    l2_block_sizes = [16, 32, 64]
    
    configurations = []
    
    # Generate all valid combinations
    for l1_block in l1_block_sizes:
        for l2_block in l2_block_sizes:
            # Direct mapped L1 (associativity = 1)
            configurations.append((l1_block, l2_block, 1, "Direct-mapped"))
            
            # Fully associative L1 (maximum associativity)
            l1_cache_size = 1024  # 1KB
            max_associativity = l1_cache_size // l1_block
            configurations.append((l1_block, l2_block, max_associativity, f"Fully-associative({max_associativity})"))
    
    results = []
    best_config = None
    best_cost = float('inf')
    successful_configs = 0
    
    print(f"\n{'='*80}")
    print(f"CACHE CONFIGURATION EXPERIMENTS FOR {binary_file}")
    print(f"Testing {len(configurations)} different configurations")
    print(f"{'='*80}")
    
    for i, (l1_block, l2_block, l1_assoc, assoc_desc) in enumerate(configurations):
        print(f"\nConfiguration {i+1}/{len(configurations)}:")
        print(f"L1: {l1_block}B blocks, {assoc_desc}")
        print(f"L2: {l2_block}B blocks, Direct-mapped")

        try:
            # Reset everything for each configuration
            init_memory()
            init_registers()
            
            # Initialize memory hierarchy with specific configuration
            # FIXED: Don't set memory_hierarchy to None before initializing
            if not init_memory_hierarchy(l1_block, l2_block, l1_assoc):
                print(f"! Failed to initialize memory hierarchy for this configuration !")
                continue
                
            # Load binary
            if load_binary(binary_file) != 0:
                print("Failed to load binary file")
                continue

            # Get the memory hierarchy instance for stats collection
            from memory_hierarchy import memory_hierarchy
            if memory_hierarchy is None:
                print("Error: Memory hierarchy is None after initialization")
                continue

            # Run simulation
            file_length = get_bin_file_length(binary_file)
            instruction_count = 0
            max_instructions = 1000  # Safety limit
            
            while get_register(15) < file_length and instruction_count < max_instructions:
                pc = get_register(15)
                
                try:
                    # Fetch instruction through cache
                    instruction = read_instruction_with_cache(pc)
                    
                    # Decode instruction
                    decoded = decode_instruction(instruction)
                    if not decoded.is_valid:
                        break

                    # Check condition and execute
                    if check(instruction, decoded):
                        execute_instruction(decoded, 1 if flag['c'] else 0)
                    
                    # Update PC if not modified by instruction
                    if get_register(15) == pc:
                        set_register(15, pc + 4)
                    
                    instruction_count += 1
                        
                except Exception as e:
                    print(f"Error at PC=0x{pc:08X}: {str(e)}")
                    break
            
            # FIXED: Collect statistics properly - verify memory_hierarchy is still valid
            if memory_hierarchy is None or not hasattr(memory_hierarchy, 'get_total_stats'):
                print("Error: Memory hierarchy lost during simulation")
                continue
                
            try:
                stats = memory_hierarchy.get_total_stats()
            except Exception as e:
                print(f"Error collecting stats: {str(e)}")
                continue
                
            config_name = f"L1:{l1_block}B-{assoc_desc}_L2:{l2_block}B-DM"
            
            # Calculate cost using the specified formula
            total_l1_misses = stats['l1_instruction_cache']['misses'] + stats['l1_data_cache']['misses']
            total_l2_misses = stats['l2_cache']['misses']
            total_writebacks = stats['l1_instruction_cache']['writebacks'] + \
                            stats['l1_data_cache']['writebacks'] + \
                            stats['l2_cache']['writebacks']
            cost = 0.5 * total_l1_misses + total_l2_misses + total_writebacks
            
            result = {
                'config_id': i+1,
                'config': config_name,
                'l1_block_size': l1_block,
                'l2_block_size': l2_block,
                'l1_associativity': l1_assoc,
                'associativity_desc': assoc_desc,
                'l1_instruction_hits': stats['l1_instruction_cache']['hits'],
                'l1_instruction_misses': stats['l1_instruction_cache']['misses'],
                'l1_data_hits': stats['l1_data_cache']['hits'],
                'l1_data_misses': stats['l1_data_cache']['misses'],
                'l2_hits': stats['l2_cache']['hits'],
                'l2_misses': stats['l2_cache']['misses'],
                'total_l1_misses': total_l1_misses,
                'total_l2_misses': total_l2_misses,
                'writebacks': total_writebacks,
                'cost': cost,
                'instruction_count': instruction_count
            }
            results.append(result)
            successful_configs += 1
            
            # Update best configuration if this one is better
            if cost < best_cost:
                best_cost = cost
                best_config = result
            
            # Print stats for this configuration
            print(f"Instructions executed: {instruction_count}")
            print(f"Cost: {cost:.2f}")
            print(f"L1 I-Cache: {stats['l1_instruction_cache']['hits']} hits, {stats['l1_instruction_cache']['misses']} misses")
            print(f"L1 D-Cache: {stats['l1_data_cache']['hits']} hits, {stats['l1_data_cache']['misses']} misses")
            print(f"L2 Cache: {stats['l2_cache']['hits']} hits, {stats['l2_cache']['misses']} misses")
            print(f"Writebacks: {total_writebacks}")
            print("✓ Configuration completed successfully")
            
        except Exception as e:
            print(f"Error in configuration {i+1}: {str(e)}")
            print("✗ Configuration failed")
            continue
    
    # Save results to file
    output_file = f"cache_results_{os.path.basename(binary_file).replace('.bin', '')}.json"
    try:
        with open(output_file, 'w') as f:
            json.dump({
                'binary_file': binary_file,
                'total_configurations_tested': successful_configs,
                'configurations': results,
                'best_configuration': best_config,
                'cost_formula': 'Cost = 0.5 * L1_misses + L2_misses + writebacks'
            }, f, indent=2)
        print(f"\nResults saved to: {output_file}")
    except Exception as e:
        print(f"Error saving results: {str(e)}")
    
    # Print summary
    print(f"\n{'='*80}")
    print("EXPERIMENT SUMMARY:")
    print(f"Tested {successful_configs} configurations successfully")
    
    if best_config:
        print(f"\nBEST CONFIGURATION:")
        print(f"Config: {best_config['config']}")
        print(f"L1 Block Size: {best_config['l1_block_size']}B")
        print(f"L2 Block Size: {best_config['l2_block_size']}B")
        print(f"L1 Associativity: {best_config['associativity_desc']}")
        print(f"Cost: {best_config['cost']:.2f}")
        print(f"L1 Misses: {best_config['total_l1_misses']}")
        print(f"L2 Misses: {best_config['total_l2_misses']}")
        print(f"Writebacks: {best_config['writebacks']}")
        print(f"Instructions: {best_config['instruction_count']}")
    else:
        print("No valid configurations found!")
    
    print(f"{'='*80}")
    return 0


def main():
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <binary_file> [--experiments]")
        print(f"  <binary_file>     : ARM binary file to simulate")
        print(f"  --experiments     : Run cache configuration experiments")
        return 1

    binary_file = sys.argv[1]
    
    # Check if binary file exists
    if not os.path.exists(binary_file):
        print(f"Error: Binary file '{binary_file}' not found!")
        return 1
    
    if len(sys.argv) > 2 and sys.argv[2] == "--experiments":
        return run_cache_experiments(binary_file)
    else:
        return run_single_simulation(binary_file)


if __name__ == "__main__":
    sys.exit(main())