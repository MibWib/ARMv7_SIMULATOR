"""
-------------------------------------------------------
[program description]
-------------------------------------------------------
Author:  Kieran Mochrie
ID:      169048254
Email:   moch8254@mylaurier.ca
__updated__ = "2025-06-24"
-------------------------------------------------------
"""
# Imports

# registers.py

NUM_REGISTERS = 16  # ARM has 16 general-purpose registers: R0–R15
PC = 15  # Program Counter is register 15

# Initialize registers array
registers = [0] * NUM_REGISTERS


def init_registers():
    global registers
    for i in range(NUM_REGISTERS):
        registers[i] = 0
    registers[PC] = 0  # Start at address 0
    #registers[6] = 9
    #registers[7] = 10


def get_register(reg_num):

    if 0 <= reg_num < NUM_REGISTERS:
        # returns 0 here
        return registers[reg_num]
    else:
        return 0


def set_register(reg_num, value):
    if 0 <= reg_num < NUM_REGISTERS:
        registers[reg_num] = value
        return


def print_registers():
    for i in range(NUM_REGISTERS):
        print(f"R{i:<2}: 0x{registers[i]:08X}, {registers[i]}")
