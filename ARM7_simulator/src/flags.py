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
from executor import execute_instruction
from registers import get_register
# Constants
flag = {
    'z': False,
    'n': False,
    'c': False,
    'v': False,

}


def check(raw, decode):
    cond = (raw >> 28) & 0xF
    rn = (raw >> 16) & 0xF
    i_bit = (raw >> 25) & 0x1
    rm = raw & 0xFF if i_bit else raw & 0xF

    conds = {
        0x0: flag['z'],                          
        0x1: not flag['z'],                       # NE
        0x2: flag['c'],                           # CS
        0x3: not flag['c'],                       # CC
        0x4: flag['n'],                           # MI
        0x5: not flag['n'],                       # PL
        0x6: flag['v'],                           # VS
        0x7: not flag['v'],                       # VC
        0x8: flag['c'] and not flag['z'],         # HI
        0x9: not flag['c'] or flag['z'],          # LS
        0xA: flag['n'] == flag['v'],              # GE
        0xB: flag['n'] != flag['v'],              # LT
        0xC: not flag['z'] and flag['n'] == flag['v'],  # GT
        0xD: flag['z'] or flag['n'] != flag['v'],       # LE
        0xE: True                                  # AL
    }

    S = (raw >> 20) & 0x1
    opcode = (raw >> 21) & 0xF

    if conds.get(cond, False):
        if S == 1 or opcode in (0x8, 0x9, 0xA, 0xB):
            flag['z'] = zero(rn, rm)
            flag['n'] = negative(rn, rm, opcode, flag['c'])
            flag['c'] = carry(rn, rm)
            flag['v'] = overflow(rn, rm)
            print(f"flags updated, Z={flag['z']}, N={flag['n']}, C={flag['c']}, V={flag['v']}")
        return True

    return False


def zero(rn, rm):
    rn1 = get_register(rn)
    rm1 = get_register(rm)

    if(rn1+rm1 == 0):
        z = True
    else:
        z = False
    return z


def negative(rn, rm, op, c):
    rn1 = get_register(rn)
    rm1 = get_register(rm)
    C = 0
    if(c):
        C = 1
    else:
        C = 0
    if op == 0x0:  # AND
        result = rn1 & rm1
    elif op == 0x1:  # EOR
        result = rn1 ^ rm1
    elif op == 0x2:  # SUB
        result = rn1 - rm1
    elif op == 0x3:  # RSB
        result = rm1-rn1
    elif op == 0x4:  # ADD
        result = rn1 + rm1
    elif op == 0x5:  # ADC
        result = rn1+rm1+C
    elif op == 0x6:  # SBC
        result = rn1-rm1-(1-C)
    elif op == 0x7:  # RSC
        result = rm1-rn1-(1-C)
    elif op == 0x8:  # TST
        result = rn1 & rm1
    elif op == 0x9:  # TEQ
        result = rn1 ^ rm1
    elif op == 0xA:  # CMP
        result = rn1 - rm1
    elif op == 0xB:  # CMN
        result = rn1 + rm1
    elif op == 0xC:  # ORR
        result = rn1 | rm1
    elif op == 0xD:  # MOV
        result = rm1
    elif op == 0xE:  # BIC
        result = rn1 & (~rm1)
    elif op == 0xF:  # MVN
        result = ~rm1 & 0xFFFFFFFF
    else:
        return False  # Unknown opcode; default to no negative flag

    return ((result >> 31) & 0x1) == 1


def carry(rn, rm):

    rn1 = get_register(rn)
    rm1 = get_register(rm)

    result = rn1+rm1
    if(result > 0xFFFFFFFF):
        c = True
    else:
        c = False
    return c


def overflow(rn, rm):
    rn1 = get_register(rn)
    rm1 = get_register(rm)

    def to_signed(val):
        return val if val < 0x80000000 else val - 0x100000000

    a = to_signed(rn1)
    b = to_signed(rm1)
    result = a + b

    # Overflow occurs if result is outside signed 32-bit range
    return result > 0x7FFFFFFF or result < -0x80000000


def func():
    """
    -------------------------------------------------------
    description
    Use: 
    -------------------------------------------------------
    Parameters:
        name - description (type)
    Returns:
        name - description (type)
    ------------------------------------------------------
    """
