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

# Constants

# decoder.py

from dataclasses import dataclass


@dataclass
class Instruction:
    raw: int
    rd: int = 0
    rn: int = 0
    rm: int = 0
    immediate: int = 0
    is_valid: bool = True
    mnemonic: str = "UNK"


def decode_instruction(raw):

    inst = Instruction(raw=raw)

    opcode = (raw >> 21) & 0xF

    i_bit = (raw >> 25) & 0x1
    #print("raw stuff", raw, inst, opcode, i_bit)
    #print("raw & 0x0c", raw & 0x0C000000)

    # Immediate or register data processing
    if (raw & 0x0C000000) == 0x00000000:

        inst.rn = (raw >> 16) & 0xF
        inst.rd = (raw >> 12) & 0xF
        if i_bit:
            inst.immediate = raw & 0xFF  # 8-bit immediate

        else:
            inst.rm = raw & 0xF  # Register operand
        # opcodes
        if opcode == 0x0:
            inst.mnemonic = "AND"

        elif opcode == 0x1:
            inst.mnemonic = "EOR"

        elif opcode == 0x2:
            inst.mnemonic = "SUB"

        elif opcode == 0x3:
            inst.mnemonic = "RSB"

        elif opcode == 0x4:
            inst.mnemonic = "ADD"

        elif opcode == 0x5:
            inst.mnemonic = "ADC"

        elif opcode == 0x6:
            inst.mnemonic = "SBC"

        elif opcode == 0x7:
            inst.mnemonic = "RSC"

        elif opcode == 0x8:
            inst.mnemonic = "TST"

        elif opcode == 0x9:
            inst.mnemonic = "TEQ"

        elif opcode == 0xA:
            inst.mnemonic = "CMP"

        elif opcode == 0xB:
            inst.mnemonic = "CMN"

        elif opcode == 0xC:
            inst.mnemonic = "ORR"

        elif opcode == 0xD:
            inst.mnemonic = "MOV"

        elif opcode == 0xE:
            inst.mnemonic = "BIC"

        else:
            inst.mnemonic = "MVN"
    else:
        inst.is_valid = False
        inst.mnemonic = "UNK"

    return inst
