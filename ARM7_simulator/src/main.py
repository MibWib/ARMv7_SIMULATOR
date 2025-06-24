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

def get_bin_file_length(filepath):
    """Returns the length of the binary file in bytes."""
    return os.path.getsize(filepath)


def main():
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <binary_file>")
        return 1

    init_memory()
    init_registers()

    if load_binary(sys.argv[1]) != 0:
        print("Failed to load binary file.")
        return 1

    filepath = sys.argv[1]
    file_length = int(get_bin_file_length(filepath))
    print("file length:", file_length)

    while get_register(15) < (file_length - 4):
        pc = get_register(15)
        instruction = read_word(pc)

        decoded = decode_instruction(instruction)
        if not decoded.is_valid:
            print(f"Halting on invalid instruction at 0x{pc:08X}")
            break

        print("decoded", decoded)

        if check(instruction, decoded):
            execute_instruction(decoded, 1 if flag['c'] else 0)

        if get_register(15) == pc:
            set_register(15, pc + 4)

    print("\nFinal Register States:")
    print_registers()
    return 0


if __name__ == "__main__":
    sys.exit(main())
