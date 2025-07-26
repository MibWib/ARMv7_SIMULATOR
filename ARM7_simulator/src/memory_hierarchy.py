# memory_hierarchy.py

from cache import Cache

class MemoryHierarchy:
    def __init__(self, l1_block_size=16, l2_block_size=32, l1_associativity=1):
        # Create L2 cache first (no next level - goes to main memory)
        self.l2_cache = Cache(16384, l2_block_size, 1)  # Direct mapped, 16KB
        
        # Create L1 caches with L2 as next level
        self.l1_instruction_cache = Cache(1024, l1_block_size, l1_associativity, next_level=self.l2_cache)
        self.l1_data_cache = Cache(1024, l1_block_size, l1_associativity, next_level=self.l2_cache)
        
        # Track if we're in data or instruction fetch mode
        self.instruction_fetch = False

    def read_instruction(self, address):
        self.instruction_fetch = True
        return self.l1_instruction_cache.read(address)

    def read_data(self, address):
        self.instruction_fetch = False
        return self.l1_data_cache.read(address)

    def write_data(self, address, data):
        self.instruction_fetch = False
        self.l1_data_cache.write(address, data)

    def get_total_stats(self):
        l1_i_stats = self.l1_instruction_cache.get_stats()
        l1_d_stats = self.l1_data_cache.get_stats()
        l2_stats = self.l2_cache.get_stats()
        
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

    def reset_stats(self):
        self.l1_instruction_cache.reset_stats()
        self.l1_data_cache.reset_stats()
        self.l2_cache.reset_stats()

    def print_stats(self):
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

# Global memory hierarchy instance
memory_hierarchy = None

def init_memory_hierarchy(l1_block_size=16, l2_block_size=32, l1_associativity=1):
    global memory_hierarchy
    memory_hierarchy = MemoryHierarchy(l1_block_size, l2_block_size, l1_associativity)

def read_instruction_with_cache(address):
    global memory_hierarchy
    if memory_hierarchy:
        return memory_hierarchy.read_instruction(address)
    else:
        from memory import read_word
        return read_word(address)

def read_data_with_cache(address):
    global memory_hierarchy
    if memory_hierarchy:
        return memory_hierarchy.read_data(address)
    else:
        from memory import read_word
        return read_word(address)

def write_data_with_cache(address, data):
    global memory_hierarchy
    if memory_hierarchy:
        memory_hierarchy.write_data(address, data)
    else:
        from memory import write_word
        write_word(address, data)