with open("test_straightline_with_cmp.bin", "wb") as f:
    f.write(bytes.fromhex("01 00 A0 E3"))  # MOV R0, #1
    f.write(bytes.fromhex("02 10 A0 E3"))  # MOV R1, #2
    f.write(bytes.fromhex("03 20 A0 E3"))  # MOV R2, #3
    f.write(bytes.fromhex("01 30 80 E0"))  # ADD R3, R0, R1
    f.write(bytes.fromhex("02 30 83 E0"))  # ADD R3, R3, R2
    f.write(bytes.fromhex("04 40 A0 E3"))  # MOV R4, #4
    f.write(bytes.fromhex("05 50 A0 E3"))  # MOV R5, #5
    f.write(bytes.fromhex("06 60 A0 E3"))  # MOV R6, #6
    f.write(bytes.fromhex("04 70 84 E0"))  # ADD R7, R4, R4
    f.write(bytes.fromhex("05 70 87 E0"))  # ADD R7, R7, R5
    f.write(bytes.fromhex("06 70 47 E0"))  # SUB R7, R7, R6  (Fixed: was C7, should be 47)
    f.write(bytes.fromhex("07 00 53 E1"))  # CMP R3, R7      (Fixed: was 07 30)
    f.write(bytes.fromhex("08 80 A0 E3"))  # MOV R8, #8
    f.write(bytes.fromhex("09 90 A0 E3"))  # MOV R9, #9
    f.write(bytes.fromhex("0A A0 A0 E3"))  # MOV R10, #10
    f.write(bytes.fromhex("0B B0 A0 E3"))  # MOV R11, #11
    f.write(bytes.fromhex("07 C0 83 E1"))  # ORR R12, R3, R7
    f.write(bytes.fromhex("08 C0 2C E0"))  # EOR R12, R12, R8 (Fixed: was C8, should be 2C)
    f.write(bytes.fromhex("09 C0 0C E0"))  # AND R12, R12, R9
    f.write(bytes.fromhex("0D D0 A0 E1"))  # MOV R13, R13
    f.write(bytes.fromhex("0E E0 A0 E1"))  # MOV R14, R14
    f.write(bytes.fromhex("FE FF FF EA"))  # B . (infinite loop)