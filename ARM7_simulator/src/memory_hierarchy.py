# memory_hierarchy.py - Fixed version with better error handling and no circular imports

from cache import Cache
from memory import read_word, write_word

class MemoryHierarchy:
    def __init__(self, l1_block_size=16, l2_block_size=32, l1_associativity=1):
        # Validate parameters
        if l1_block_size not in [4, 8, 16, 32]:
            raise ValueError(f"Invalid L1 block size: {l1_block_size}. Must be 4, 8, 16, or 32")
        if l2_block_size not in [16, 32, 64]:
            raise ValueError(f"Invalid L2 block size: {l2_block_size}. Must be 16, 32, or 64")
            
        # Calculate L1 associativity for "fully associative" case
        l1_cache_size = 1024  # 1KB
        if l1_associativity > 1:
            # For fully associative, use maximum possible associativity
            max_associativity = l1_cache_size // l1_block_size
            l1_associativity = min(l1_associativity, max_associativity)
            
        print(f"Initializing Memory Hierarchy:")
        print(f"  L1 I-Cache: {l1_cache_size}B, {l1_block_size}B blocks, {l1_associativity}-way")
        print(f"  L1 D-Cache: {l1_cache_size}B, {l1_block_size}B blocks, {l1_associativity}-way")
        print(f"  L2 Cache: 16KB, {l2_block_size}B blocks, Direct-mapped")
            
        try:
            # Create L2 cache first (no next level - goes to main memory)
            self.l2_cache = Cache(16384, l2_block_size, 1, "write_back")  # Direct mapped, 16KB
            
            # Create L1 caches with L2 as next level
            self.l1_instruction_cache = Cache(1024, l1_block_size, l1_associativity, "write_back", self.l2_cache)
            self.l1_data_cache = Cache(1024, l1_block_size, l1_associativity, "write_back", self.l2_cache)

            # Initialize stats
            self.reset_stats()
            self.initialized = True  # Mark as initialized
            print("Memory hierarchy initialized successfully")
            
        except Exception as e:
            print(f"Error initializing caches: {str(e)}")
            self.initialized = False
            raise

    def reset_stats(self):
        """Reset all cache statistics"""
        if hasattr(self, 'l1_instruction_cache') and self.l1_instruction_cache:
            self.l1_instruction_cache.reset_stats()
        if hasattr(self, 'l1_data_cache') and self.l1_data_cache:
            self.l1_data_cache.reset_stats()
        if hasattr(self, 'l2_cache') and self.l2_cache:
            self.l2_cache.reset_stats()

    def read_instruction(self, address):
        """Read instruction from L1 instruction cache"""
        if not hasattr(self, 'l1_instruction_cache') or not self.l1_instruction_cache:
            raise RuntimeError("Instruction cache not initialized")
        return self.l1_instruction_cache.read(address)

    def read_data(self, address):
        """Read data from L1 data cache"""
        if not hasattr(self, 'l1_data_cache') or not self.l1_data_cache:
            raise RuntimeError("Data cache not initialized")
        return self.l1_data_cache.read(address)

    def write_data(self, address, data):
        """Write data to L1 data cache"""
        if not hasattr(self, 'l1_data_cache') or not self.l1_data_cache:
            raise RuntimeError("Data cache not initialized")
        self.l1_data_cache.write(address, data)

    def get_total_stats(self):
        """Get combined statistics from all cache levels"""
        if not all(hasattr(self, attr) and getattr(self, attr) is not None 
                  for attr in ['l1_instruction_cache', 'l1_data_cache', 'l2_cache']):
            raise RuntimeError("Cache hierarchy not properly initialized")
            
        try:
            l1_i_stats = self.l1_instruction_cache.get_stats()
            l1_d_stats = self.l1_data_cache.get_stats()
            l2_stats = self.l2_cache.get_stats()
        except Exception as e:
            raise RuntimeError(f"Error getting cache stats: {str(e)}")
        
        total_l1_misses = l1_i_stats['misses'] + l1_d_stats['misses']
        total_l2_misses = l2_stats['misses']
        total_writebacks = l1_i_stats['writebacks'] + l1_d_stats['writebacks'] + l2_stats['writebacks']
        
        cost = 0.5 * total_l1_misses + total_l2_misses + total_writebacks
        
        return {
            'l1_instruction_cache': l1_i_stats,
            'l1_data_cache': l1_d_stats,
            'l2_cache': l2_stats,
            'total_l1_misses': total_l1_misses,
            'total_l2_misses': total_l2_misses,
            'total_writebacks': total_writebacks,
            'cost': cost
        }

    def print_stats(self):
        """Print detailed cache statistics"""
        try:
            stats = self.get_total_stats()
            print(f"\n=== Cache Statistics ===")
            print(f"L1 Instruction Cache: {stats['l1_instruction_cache']['hits']} hits, {stats['l1_instruction_cache']['misses']} misses (Hit Rate: {stats['l1_instruction_cache']['hit_rate']:.3f})")
            print(f"L1 Data Cache: {stats['l1_data_cache']['hits']} hits, {stats['l1_data_cache']['misses']} misses (Hit Rate: {stats['l1_data_cache']['hit_rate']:.3f})")
            print(f"L2 Cache: {stats['l2_cache']['hits']} hits, {stats['l2_cache']['misses']} misses (Hit Rate: {stats['l2_cache']['hit_rate']:.3f})")
            print(f"Total L1 Misses: {stats['total_l1_misses']}")
            print(f"Total L2 Misses: {stats['total_l2_misses']}")
            print(f"Total Writebacks: {stats['total_writebacks']}")
            print(f"Cost: {stats['cost']:.2f}")
            print("========================\n")
        except Exception as e:
            print(f"Error printing stats: {str(e)}")

# Global memory hierarchy instance
memory_hierarchy = None

def init_memory_hierarchy(l1_block_size=16, l2_block_size=32, l1_associativity=1):
    """Initialize the memory hierarchy with given parameters"""
    global memory_hierarchy
    try:
        # Create new instance (don't set to None first - this was the main bug!)
        new_hierarchy = MemoryHierarchy(l1_block_size, l2_block_size, l1_associativity)
        
        # Only assign to global variable after successful creation
        memory_hierarchy = new_hierarchy
        return True
        
    except Exception as e:
        print(f"Failed to initialize memory hierarchy: {str(e)}")
        memory_hierarchy = None
        return False

def check_initialized():
    """Check if memory hierarchy is properly initialized"""
    if memory_hierarchy is None:
        raise RuntimeError("Memory hierarchy not initialized. Call init_memory_hierarchy() first.")
    if not hasattr(memory_hierarchy, 'initialized') or not memory_hierarchy.initialized:
        raise RuntimeError("Memory hierarchy initialization incomplete.")

def read_instruction_with_cache(address):
    """Read instruction through cache hierarchy"""
    check_initialized()
    return memory_hierarchy.read_instruction(address)

def read_data_with_cache(address):
    """Read data through cache hierarchy"""
    check_initialized()
    return memory_hierarchy.read_data(address)

def write_data_with_cache(address, data):
    """Write data through cache hierarchy"""
    check_initialized()
    memory_hierarchy.write_data(address, data)