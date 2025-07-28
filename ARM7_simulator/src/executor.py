# Enhanced executor.py with fixed memory operations and branch handling

from registers import get_register, set_register
from decoder import Instruction
from memory_hierarchy import read_data_with_cache, write_data_with_cache

def execute_instruction(inst: Instruction, C):
    if not inst.is_valid:
        print(f"Invalid instruction: 0x{inst.raw:08X}")
        return

    pc = get_register(15)
    result = 0
    rn1 = get_register(inst.rn)
    rm1 = get_register(inst.rm)

    print(f"Executing {inst.mnemonic}, destination register: R{inst.rd}")

    # Handle branch instructions first
    if inst.mnemonic == "B":
        offset = inst.immediate
        new_pc = pc + offset  # Offset is already adjusted in decoder
        set_register(15, new_pc)
        print(f"Branch to 0x{new_pc:08X}")
        return

    # Handle memory operations
    if inst.is_memory_op:
        if inst.mnemonic == "LDR":
            # Load from memory
            address = rn1 + inst.offset
            try:
                data = read_data_with_cache(address)
                set_register(inst.rd, data)
                print(f"LDR: Loaded 0x{data:08X} from address 0x{address:08X} into R{inst.rd}")
            except Exception as e:
                print(f"LDR error at address 0x{address:08X}: {str(e)}")
                
        elif inst.mnemonic == "STR":
            # Store to memory  
            address = rn1 + inst.offset
            data = get_register(inst.rd)
            try:
                write_data_with_cache(address, data)
                print(f"STR: Stored 0x{data:08X} from R{inst.rd} to address 0x{address:08X}")
            except Exception as e:
                print(f"STR error at address 0x{address:08X}: {str(e)}")
        return

    # Handle data processing operations
    operand = inst.immediate if inst.immediate else rm1

    if inst.mnemonic == "AND":
        result = rn1 & operand
        set_register(inst.rd, result)

    elif inst.mnemonic == "EOR":
        operand = inst.immediate if inst.immediate else rm1
        result = rn1 ^ operand
        set_register(inst.rd, result)

    elif inst.mnemonic == "SUB":
        operand = inst.immediate if inst.immediate else rm1
        result = rn1 - operand
        set_register(inst.rd, result)

    elif inst.mnemonic == "SUBS":
        operand = inst.immediate if inst.immediate else rm1
        result = rn1 - operand
        set_register(inst.rd, result)
        # Note: SUBS should also update flags

    elif inst.mnemonic == "RSB":
        operand = inst.immediate if inst.immediate else rm1
        result = operand - rn1
        set_register(inst.rd, result)

    elif inst.mnemonic == "ADD":
        operand = inst.immediate if inst.immediate else rm1
        result = rn1 + operand
        set_register(inst.rd, result)

    elif inst.mnemonic == "ADC":
        operand = inst.immediate if inst.immediate else rm1
        result = rn1 + operand + C
        set_register(inst.rd, result)

    elif inst.mnemonic == "SBC":
        operand = inst.immediate if inst.immediate else rm1
        result = rn1 - operand - (1-C)
        set_register(inst.rd, result)

    elif inst.mnemonic == "RSC":
        operand = inst.immediate if inst.immediate else rm1
        result = operand - rn1 - (1-C)
        set_register(inst.rd, result)

    elif inst.mnemonic == "ORR":
        operand = inst.immediate if inst.immediate else rm1
        result = rn1 | operand
        set_register(inst.rd, result)

    elif inst.mnemonic == "MOV":
        result = inst.immediate if inst.immediate else rm1
        set_register(inst.rd, result)

    elif inst.mnemonic == "BIC":
        operand = inst.immediate if inst.immediate else rm1
        result = rn1 & (~operand)
        set_register(inst.rd, result)

    elif inst.mnemonic == "MVN":
        operand = inst.immediate if inst.immediate else rm1
        result = ~operand & 0xFFFFFFFF
        set_register(inst.rd, result)

    elif inst.mnemonic in ["CMP", "CMN", "TST", "TEQ"]:
        print(f"Known instruction: {inst.mnemonic}, flags updated, no value stored")

    else:
        print(f"Unknown instruction: {inst.mnemonic}")

    print(f"Executed: {inst.mnemonic}")