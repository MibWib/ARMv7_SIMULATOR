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
    if i_bit:
        rm = raw & 0xFF  # 8-bit immediate
        print("immediate=1")
    else:
        rm = raw & 0xF
        print("immediate=0")
    # have all flags checked here
    # equal
    conds = {
        0x0: flag['z'],  # equal EQ
        0x1: not flag['z'],  # not equal NE
        0x2: flag['c'],  # carry set CS
        0x3: not flag['c'],  # carry clear CC
        0x4: flag['n'],  # negative MI
        0x5: not flag['n'],  # positive or 0 PL
        0x6: flag['v'],  # overflow VS
        0x7: not flag['v'],  # no overflow VC
        0x8: flag['c'] and not flag['z'],  # unsigned higher HI
        0x9: not flag['c'] or flag['z'],  # unsigned lower/same LS
        0xA: flag['n'] == flag['v'],  # signed greater than or equal GE
        0xB: flag['n'] != flag['v'],  # signed less than LT
        # signed greater than GT
        0xC: not flag['z'] and flag['n'] == flag['v'],
        # signed less than or equal LE
        0xD: flag['z'] or flag['n'] != flag['v'],
        0xE: True  # always execute

    }
    S = (raw >> 20) & 0x1  # if S=1 set new flags
    opcode = (raw >> 21) & 0xF
    # sets flags if S bit is true AND the condition is met or if any flag setting command is used AND the condition is met
    print("S=", S)
    if((S == 1 & conds.get(cond, False)) or (opcode == 0xB & conds.get(cond, False)) or (opcode == 0xA & conds.get(cond, False))
            or (opcode == 0x9 & conds.get(cond, False)) or (opcode == 0x8 & conds.get(cond, False))):

        flag['z'] = zero(rn, rm)
        flag['n'] = negative(rn, rm, opcode, flag['c'])
        flag['c'] = carry(rn, rm)
        flag['v'] = overflow(rn, rm)
        print(
            f"flags updated, Z={flag['z']}, N={flag['n']}, C={flag['c']}, V={flag['v']}")
    if (conds.get(cond) == True):  # no place to store with cmp or cmn

        execute_instruction(decode, 1 if flag['c'] else 0)


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
