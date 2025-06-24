"""
-------------------------------------------------------
[program description]
-------------------------------------------------------
Author:  Kieran Mochrie
ID:      169048254
Email:   moch8254@mylaurier.ca
__updated__ = "2025-06-23"
-------------------------------------------------------
"""
# Imports

# Constants

# memory.py

MEMORY_SIZE = 4096  # Or whatever size you need
memory = [0] * MEMORY_SIZE  # Byte-addressable memory


def init_memory():
    global memory
    memory = [0] * MEMORY_SIZE


def read_word(address):
    #address is pc
    if address + 3 >= MEMORY_SIZE:
        return 0

    #print(memory[address], memory[address] << 24, memory[address+1] << 16)
    #print(memory[address+2], memory[address+2] << 8, memory[address+3])

    return (memory[address] << 24) | (memory[address + 1] << 16) | \
           (memory[address + 2] << 8) | memory[address + 3]


def write_word(address, value):
    if address + 3 >= MEMORY_SIZE:
        return
    memory[address] = (value >> 24) & 0xFF
    memory[address + 1] = (value >> 16) & 0xFF
    memory[address + 2] = (value >> 8) & 0xFF
    memory[address + 3] = value & 0xFF


def print_memory(start, end):
    for i in range(start, min(end + 1, MEMORY_SIZE - 3), 4):
        word = read_word(i)
        print(f"0x{i:04X}: 0x{word:08X}")
