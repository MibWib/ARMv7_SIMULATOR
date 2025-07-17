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
    def __init__(self, size, block_size=16, associativity=1, mapping='direct'):
        self.size = size
        self.block_size = block_size
        self.associativity = associativity
        self.mapping = mapping  # 'direct' or 'fully'
        self.blocks = {}

        self.miss_count = 0
        self.write_back_count = 0
        self.hits = 0
        self.misses = 0
        self.writebacks = 0
        self.offset_bits = int(math.log2(self.block_size))
        num_sets = self.size // (self.block_size * self.associativity)
        self.index_bits = int(math.log2(num_sets)) if num_sets > 1 else 0

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

    def load_block_from_memory(self, address, block):
        block_address = address & ~((1 << self.offset_bits) - 1)
        for i in range(self.block_size // 4):
            word_addr = block_address + (i * 4)
            block.data[i] = mem_read_word(word_addr)

    def write_block_to_memory(self, address, block):
        block_address = address & ~((1 << self.offset_bits) - 1)
        for i in range(self.block_size // 4):
            word_addr = block_address + (i * 4)
            mem_write_word(word_addr, block.data[i])

    def read(self, address):
        block_addr = address // self.block_size * self.block_size
        if block_addr not in self.blocks:
            self.miss_count += 1
            return None
        return self.blocks[block_addr]

    def write(self, address, data):
        block_addr = address // self.block_size * self.block_size
        if block_addr in self.blocks:
            self.write_back_count += 1
        self.blocks[block_addr] = data

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
