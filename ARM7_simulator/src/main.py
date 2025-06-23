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
# imports
# Constants
import sys
from file_reader import load_binary
from memory import init_memory, read_word
from registers import init_registers, get_register, set_register, print_registers
from decoder import decode_instruction
from executor import execute_instruction
from flags import check


def main():
    # "C:\Users\kiera\eclipse2\ws\ARM7_simulator\src\main.py" "C:\Users\kiera\eclipse2\ws\ARM7_simulator\src\test_program.bin"

    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <binary_file>")
        return 1

    init_memory()

    init_registers()
    x = 0
    if load_binary(sys.argv[1], x) != 0:
        print("Failed to load binary file.")
        return 1
    x = 1
    loop = True
    # Start executing from PC = 0
    while loop:
        pc = get_register(15)  # PC is R15

        instruction = read_word(pc)
        print("instructions", instruction)

        decoded = decode_instruction(instruction)
        if not decoded.is_valid:
            print(f"Halting on invalid instruction at 0x{pc:08X}")
            break

        print("decoded", decoded)

        check(instruction, decoded)  # check flags for instruction

        set_register(15, pc + 4)  # Move to next instruction
        # breaks infinite while loop i made on accident
        if load_binary(sys.argv[1], x) != 0:
            loop = False

    print("\nFinal Register States:")
    print_registers()
    return 0


if __name__ == "__main__":
    sys.exit(main())
