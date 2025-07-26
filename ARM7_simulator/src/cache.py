# cache.py

import math
from memory import read_word as mem_read_word, write_word as mem_write_word

class CacheBlock:
    def __init__(self, block_size):
        self.valid = False
        self.dirty = False
        self.tag = 0
        self.data = [0] * block_size
        self.lru_counter = 0

class Cache:
    def __init__(self, cache_size, block_size, associativity, write_policy="write_back", next_level=None):
        self.cache_size = cache_size
        self.block_size = block_size
        self.associativity = associativity
        self.write_policy = write_policy
        self.next_level = next_level  # Next level cache (L2 for L1, None for L2)
        
        # Calculate cache parameters
        self.num_blocks = cache_size // block_size
        self.num_sets = self.num_blocks // associativity
        self.offset_bits = int(math.log2(block_size))
        self.index_bits = int(math.log2(self.num_sets)) if self.num_sets > 1 else 0
        self.tag_bits = 32 - self.offset_bits - self.index_bits
        
        # Initialize cache blocks
        self.blocks = []
        for i in range(self.num_sets):
            set_blocks = []
            for j in range(associativity):
                set_blocks.append(CacheBlock(block_size // 4))  # 4 bytes per word
            self.blocks.append(set_blocks)
        
        # Statistics
        self.hits = 0
        self.misses = 0
        self.writebacks = 0
        self.lru_counter = 0

    def get_cache_info(self, address):
        offset = address & ((1 << self.offset_bits) - 1)
        index = (address >> self.offset_bits) & ((1 << self.index_bits) - 1) if self.index_bits > 0 else 0
        tag = address >> (self.offset_bits + self.index_bits)
        word_offset = offset // 4
        return tag, index, word_offset

    def find_block(self, tag, index):
        for i, block in enumerate(self.blocks[index]):
            if block.valid and block.tag == tag:
                return i
        return -1

    def find_lru_block(self, index):
        lru_block = 0
        min_counter = self.blocks[index][0].lru_counter
        for i, block in enumerate(self.blocks[index]):
            if block.lru_counter < min_counter:
                min_counter = block.lru_counter
                lru_block = i
        return lru_block

    def update_lru(self, index, block_idx):
        self.lru_counter += 1
        self.blocks[index][block_idx].lru_counter = self.lru_counter

    def load_block_from_next_level(self, address, block):
        """Load block from next level cache or main memory"""
        block_address = address & ~((1 << self.offset_bits) - 1)
        
        if self.next_level:
            # Load from next level cache
            for i in range(self.block_size // 4):
                word_addr = block_address + (i * 4)
                block.data[i] = self.next_level.read(word_addr)
        else:
            # Load from main memory
            for i in range(self.block_size // 4):
                word_addr = block_address + (i * 4)
                block.data[i] = mem_read_word(word_addr)

    def write_block_to_next_level(self, address, block):
        """Write block to next level cache or main memory"""
        block_address = address & ~((1 << self.offset_bits) - 1)
        
        if self.next_level:
            # Write to next level cache
            for i in range(self.block_size // 4):
                word_addr = block_address + (i * 4)
                self.next_level.write(word_addr, block.data[i])
        else:
            # Write to main memory
            for i in range(self.block_size // 4):
                word_addr = block_address + (i * 4)
                mem_write_word(word_addr, block.data[i])

    def read(self, address):
        tag, index, word_offset = self.get_cache_info(address)
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
        tag, index, word_offset = self.get_cache_info(address)
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
            
            # Load new block from next level
            self.load_block_from_next_level(address, block)
            block.valid = True
            block.tag = tag
            block.data[word_offset] = data
            block.dirty = True
            self.update_lru(index, lru_idx)

    def get_stats(self):
        return {
            'hits': self.hits,
            'misses': self.misses,
            'writebacks': self.writebacks,
            'hit_rate': self.hits / (self.hits + self.misses) if (self.hits + self.misses) > 0 else 0
        }

    def reset_stats(self):
        self.hits = 0
        self.misses = 0
        self.writebacks = 0