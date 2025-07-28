# cache.py - Fixed version with improved error handling and bounds checking

import math
from memory import read_word as mem_read_word, write_word as mem_write_word

class CacheBlock:
    def __init__(self, block_size_words):
        self.valid = False
        self.dirty = False
        self.tag = 0
        self.data = [0] * max(1, block_size_words)  # Ensure at least 1 word
        self.lru_counter = 0

class Cache:
    def __init__(self, cache_size, block_size, associativity, write_policy="write_back", next_level=None):
        # Validate inputs
        if cache_size <= 0 or block_size <= 0 or associativity <= 0:
            raise ValueError(f"Cache parameters must be positive: cache_size={cache_size}, block_size={block_size}, associativity={associativity}")
        if cache_size % block_size != 0:
            raise ValueError(f"Cache size ({cache_size}) must be divisible by block size ({block_size})")
        if block_size % 4 != 0:
            raise ValueError(f"Block size ({block_size}) must be divisible by 4 (word size)")
        
        self.cache_size = cache_size
        self.block_size = block_size
        self.associativity = associativity
        self.write_policy = write_policy
        self.next_level = next_level  # Next level cache or main memory
        
        # Calculate cache parameters
        self.num_blocks = cache_size // block_size
        self.num_sets = self.num_blocks // associativity
        
        if self.num_sets <= 0:
            raise ValueError(f"Invalid configuration: num_sets={self.num_sets}")
        
        # Calculate bit fields
        self.offset_bits = int(math.log2(block_size)) if block_size > 1 else 0
        self.index_bits = int(math.log2(self.num_sets)) if self.num_sets > 1 else 0
        self.tag_bits = 32 - (self.offset_bits + self.index_bits)
        
        # Ensure valid bit field sizes
        if self.offset_bits < 0 or self.index_bits < 0 or self.tag_bits <= 0:
            raise ValueError(f"Invalid bit field configuration: offset={self.offset_bits}, index={self.index_bits}, tag={self.tag_bits}")
        
        # Initialize cache blocks
        self.blocks = []
        words_per_block = max(1, block_size // 4)  # Each word is 4 bytes, ensure at least 1
        
        for _ in range(self.num_sets):
            set_blocks = []
            for _ in range(associativity):
                set_blocks.append(CacheBlock(words_per_block))
            self.blocks.append(set_blocks)
        
        # Initialize statistics
        self.reset_stats()
        
        print(f"Cache initialized: {cache_size}B, {block_size}B blocks, {associativity}-way, {self.num_sets} sets")

    def reset_stats(self):
        """Reset all statistics counters"""
        self.hits = 0
        self.misses = 0
        self.writebacks = 0
        self.access_count = 0
        self.lru_counter = 0  # Global counter for LRU

    def get_cache_info(self, address):
        """Extract tag, index, and word offset from address"""
        # Ensure address is non-negative
        address = address & 0xFFFFFFFF
        
        # Handle edge cases
        if self.offset_bits == 0:
            offset = 0
        else:
            offset_mask = (1 << self.offset_bits) - 1
            offset = address & offset_mask
            
        if self.index_bits == 0:
            index = 0
        else:
            index_mask = (1 << self.index_bits) - 1
            index = (address >> self.offset_bits) & index_mask
        
        tag = address >> (self.offset_bits + self.index_bits)
        word_offset = offset // 4  # Convert byte offset to word offset
        
        # Bounds checking
        if index >= len(self.blocks):
            print(f"Warning: Index {index} out of bounds, using 0")
            index = 0
        if word_offset >= len(self.blocks[0][0].data):
            print(f"Warning: Word offset {word_offset} out of bounds, using 0")
            word_offset = 0
        
        return tag, index, word_offset

    def find_block(self, tag, index):
        """Find a matching block in the set, return its position or -1 if not found"""
        if index >= len(self.blocks):
            return -1
            
        for i, block in enumerate(self.blocks[index]):
            if block.valid and block.tag == tag:
                return i
        return -1

    def find_lru_block(self, index):
        """Find the LRU block in the set"""
        if index >= len(self.blocks) or len(self.blocks[index]) == 0:
            return 0
            
        lru_block = 0
        min_counter = self.blocks[index][0].lru_counter
        
        for i, block in enumerate(self.blocks[index]):
            if block.lru_counter < min_counter:
                min_counter = block.lru_counter
                lru_block = i
        return lru_block

    def update_lru(self, index, block_idx):
        """Update LRU counters"""
        if index < len(self.blocks) and block_idx < len(self.blocks[index]):
            self.lru_counter += 1
            self.blocks[index][block_idx].lru_counter = self.lru_counter

    def load_block_from_next_level(self, address, block):
        """Load a block from next level cache or main memory"""
        # Align address to block boundary
        if self.offset_bits > 0:
            block_address = address & ~((1 << self.offset_bits) - 1)
        else:
            block_address = address
        
        words_per_block = max(1, self.block_size // 4)
        
        # Ensure block.data has enough space
        if len(block.data) < words_per_block:
            block.data = [0] * words_per_block
        
        if self.next_level:
            # Load from next level cache
            for i in range(words_per_block):
                word_addr = block_address + (i * 4)
                try:
                    block.data[i] = self.next_level.read(word_addr)
                except Exception as e:
                    # If next level fails, try main memory
                    try:
                        block.data[i] = mem_read_word(word_addr)
                    except:
                        block.data[i] = 0  # Default value on error
        else:
            # Load from main memory
            for i in range(words_per_block):
                word_addr = block_address + (i * 4)
                try:
                    block.data[i] = mem_read_word(word_addr)
                except:
                    block.data[i] = 0  # Default value on error

    def write_block_to_next_level(self, address, block):
        """Write a block to next level cache or main memory"""
        # Align address to block boundary
        if self.offset_bits > 0:
            block_address = address & ~((1 << self.offset_bits) - 1)
        else:
            block_address = address
        
        words_per_block = min(len(block.data), self.block_size // 4)
        
        if self.next_level:
            # Write to next level cache
            for i in range(words_per_block):
                word_addr = block_address + (i * 4)
                try:
                    self.next_level.write(word_addr, block.data[i])
                except Exception as e:
                    # If next level fails, write to main memory
                    try:
                        mem_write_word(word_addr, block.data[i])
                    except:
                        pass  # Ignore write errors
        else:
            # Write to main memory
            for i in range(words_per_block):
                word_addr = block_address + (i * 4)
                try:
                    mem_write_word(word_addr, block.data[i])
                except:
                    pass  # Ignore write errors

    def read(self, address):
        """Read data from cache"""
        self.access_count += 1
        tag, index, word_offset = self.get_cache_info(address)
        
        # Bounds checking
        if index >= len(self.blocks) or word_offset >= len(self.blocks[index][0].data):
            # Fallback to main memory for invalid cache access
            self.misses += 1
            try:
                return mem_read_word(address)
            except:
                return 0
        
        block_idx = self.find_block(tag, index)
        
        if block_idx != -1:  # Cache hit
            self.hits += 1
            block = self.blocks[index][block_idx]
            self.update_lru(index, block_idx)
            return block.data[word_offset]
        else:  # Cache miss
            self.misses += 1
            # Find LRU block to replace
            lru_idx = self.find_lru_block(index)
            block = self.blocks[index][lru_idx]
            
            # Write back if dirty
            if block.valid and block.dirty:
                old_address = (block.tag << (self.offset_bits + self.index_bits)) | (index << self.offset_bits)
                self.write_block_to_next_level(old_address, block)
                self.writebacks += 1
            
            # Load new block from next level
            self.load_block_from_next_level(address, block)
            block.valid = True
            block.dirty = False
            block.tag = tag
            self.update_lru(index, lru_idx)
            
            return block.data[word_offset]

    def write(self, address, data):
        """Write data to cache"""
        self.access_count += 1
        tag, index, word_offset = self.get_cache_info(address)
        
        # Bounds checking
        if index >= len(self.blocks) or word_offset >= len(self.blocks[index][0].data):
            # Fallback to main memory for invalid cache access
            self.misses += 1
            try:
                mem_write_word(address, data)
            except:
                pass
            return
        
        block_idx = self.find_block(tag, index)
        
        if block_idx != -1:  # Cache hit
            self.hits += 1
            block = self.blocks[index][block_idx]
            block.data[word_offset] = data
            block.dirty = True
            self.update_lru(index, block_idx)
        else:  # Cache miss
            self.misses += 1
            # Find LRU block to replace
            lru_idx = self.find_lru_block(index)
            block = self.blocks[index][lru_idx]
            
            # Write back if dirty
            if block.valid and block.dirty:
                old_address = (block.tag << (self.offset_bits + self.index_bits)) | (index << self.offset_bits)
                self.write_block_to_next_level(old_address, block)
                self.writebacks += 1
            
            # Load new block from next level (write-allocate policy)
            self.load_block_from_next_level(address, block)
            block.valid = True
            block.tag = tag
            block.data[word_offset] = data
            block.dirty = True
            self.update_lru(index, lru_idx)

    def get_stats(self):
        """Return cache statistics"""
        total_accesses = self.hits + self.misses
        hit_rate = self.hits / total_accesses if total_accesses > 0 else 0
        
        return {
            'hits': self.hits,
            'misses': self.misses,
            'writebacks': self.writebacks,
            'access_count': self.access_count,
            'hit_rate': hit_rate
        }