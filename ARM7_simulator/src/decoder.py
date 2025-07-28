# Enhanced decoder.py with LDR/STR support

from dataclasses import dataclass

@dataclass
class Instruction:
    raw: int
    rd: int = 0
    rn: int = 0
    rm: int = 0
    immediate: int = 0
    offset: int = 0  # For memory instructions
    is_valid: bool = True
    mnemonic: str = "UNK"
    is_memory_op: bool = False  # Flag for memory operations

def decode_instruction(raw):
    inst = Instruction(raw=raw)

    # Extract common fields
    cond = (raw >> 28) & 0xF
    opcode = (raw >> 21) & 0xF
    i_bit = (raw >> 25) & 0x1
    inst.rn = (raw >> 16) & 0xF
    inst.rd = (raw >> 12) & 0xF

    # Branch instruction
    if (raw & 0x0E000000) == 0x0A000000:
        inst.mnemonic = "B"
        inst.immediate = raw & 0x00FFFFFF
        if inst.immediate & 0x00800000:
            inst.immediate |= 0xFF000000 
        inst.immediate <<= 2
        inst.rd = 15  # target is PC
        return inst

    # Single data transfer (LDR/STR)
    elif (raw & 0x0C000000) == 0x04000000:
        inst.is_memory_op = True
        l_bit = (raw >> 20) & 0x1  # Load/Store bit
        
        if l_bit:
            inst.mnemonic = "LDR"
        else:
            inst.mnemonic = "STR"
            
        # Extract 12-bit immediate offset
        inst.offset = raw & 0xFFF
        u_bit = (raw >> 23) & 0x1  # Up/Down bit
        if not u_bit:  # Down bit - negative offset
            inst.offset = -inst.offset
            
        return inst

    # Data-processing instruction  
    elif (raw & 0x0C000000) == 0x00000000:
        if i_bit:
            # Immediate value with rotation
            immediate_8 = raw & 0xFF
            rotate_imm = (raw >> 8) & 0xF
            # Apply rotation: rotate right by (rotate_imm * 2) bits
            rotate_amount = rotate_imm * 2
            if rotate_amount == 0:
                inst.immediate = immediate_8
            else:
                # Rotate right
                inst.immediate = ((immediate_8 >> rotate_amount) | (immediate_8 << (32 - rotate_amount))) & 0xFFFFFFFF
        else:
            inst.rm = raw & 0xF

        if opcode == 0x0: inst.mnemonic = "AND"
        elif opcode == 0x1: inst.mnemonic = "EOR"
        elif opcode == 0x2: 
            s_bit = (raw >> 20) & 0x1
            if s_bit:
                inst.mnemonic = "SUBS"
            else:
                inst.mnemonic = "SUB"
        elif opcode == 0x3: inst.mnemonic = "RSB"
        elif opcode == 0x4: inst.mnemonic = "ADD"
        elif opcode == 0x5: inst.mnemonic = "ADC"
        elif opcode == 0x6: inst.mnemonic = "SBC"
        elif opcode == 0x7: inst.mnemonic = "RSC"
        elif opcode == 0x8: inst.mnemonic = "TST"
        elif opcode == 0x9: inst.mnemonic = "TEQ"
        elif opcode == 0xA: inst.mnemonic = "CMP"
        elif opcode == 0xB: inst.mnemonic = "CMN"
        elif opcode == 0xC: inst.mnemonic = "ORR"
        elif opcode == 0xD: inst.mnemonic = "MOV"
        elif opcode == 0xE: inst.mnemonic = "BIC"
        elif opcode == 0xF: inst.mnemonic = "MVN"

    else:
        inst.is_valid = False
        inst.mnemonic = "UNK"

    return inst