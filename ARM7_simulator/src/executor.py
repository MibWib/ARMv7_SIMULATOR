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

# executor.py

from registers import get_register, set_register
from decoder import Instruction


def execute_instruction(inst: Instruction, C):
    if not inst.is_valid:
        print(f"Invalid instruction: 0x{inst.raw:08X}")
        return

    result = 0
    rn1 = get_register(inst.rn)
    rm1 = get_register(inst.rm)

    print("destination register", inst.rd)

    if inst.mnemonic == "AND":
        operand = inst.immediate if inst.immediate else rm1
        result = rn1 & rm1

    elif inst.mnemonic == "B":
        pc = get_register(15)
        set_register(15, pc + inst.immediate)

    elif inst.mnemonic == "EOR":
        operand = inst.immediate if inst.immediate else rm1
        result = rn1 ^ rm1
        set_register(inst.rd, result)

    elif inst.mnemonic == "SUB":
        operand = inst.immediate if inst.immediate else rm1
        result = rn1 - operand
        set_register(inst.rd, result)

    elif inst.mnemonic == "RSB":
        operand = inst.immediate if inst.immediate else rm1
        result = operand-rn1
        set_register(inst.rd, result)

    elif inst.mnemonic == "ADD":
        operand = inst.immediate if inst.immediate else rm1
        result = rn1 + operand
        set_register(inst.rd, result)

    elif inst.mnemonic == "ADC":
        operand = inst.immediate if inst.immediate else rm1
        result = rn1 + operand+C
        set_register(inst.rd, result)

    elif inst.mnemonic == "SBC":
        operand = inst.immediate if inst.immediate else rm1
        result = rn1 - operand-(1-C)
        set_register(inst.rd, result)

    elif inst.mnemonic == "RSC":
        operand = inst.immediate if inst.immediate else rm1
        result = operand-rn1-(1-C)
        set_register(inst.rd, result)
    # CMP, CMN, TEQ and TST would go here if they stored values
    elif inst.mnemonic == "ORR":
        operand = inst.immediate if inst.immediate else rm1
        result = rn1 | rm1
        set_register(inst.rd, result)

    elif inst.mnemonic == "MOV":
        result = inst.immediate if inst.immediate else rm1
        set_register(inst.rd, result)

    elif inst.mnemonic == "BIC":
        operand = inst.immediate if inst.immediate else rm1
        result = rn1 & (~rm1)
        set_register(inst.rd, result)

    elif inst.mnemonic == "MVN":
        result = ~rn1 & 0xFFFFFFFF
        set_register(inst.rd, result)

    elif inst.mnemonic == "CMP" or inst.mnemonic == "CMN" or inst.mnemonic == "TST"or inst.mnemonic == "TEQ":
        print(
            f"Known instruction: {inst.mnemonic}, flags updated, no value stored")

    else:
        print(f"Unknown instruction: {inst.mnemonic}")

    print(f"Executed: {inst.mnemonic}")
