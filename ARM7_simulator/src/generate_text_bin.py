with open("test_custom.bin", "wb") as f:
    f.write(bytes.fromhex("01 00 A0 E3"))  # MOV R0, #1
    f.write(bytes.fromhex("02 10 80 E2"))  # ADD R1, R0, #2
    f.write(bytes.fromhex("05 20 A0 E3"))  # MOV R2, #5
    f.write(bytes.fromhex("02 30 42 E2"))  # SUB R3, R2, #2
    f.write(bytes.fromhex("03 30 53 E3"))  # CMP R3, #3
    f.write(bytes.fromhex("00 40 83 E0"))  # ADD R4, R3, R0
    f.write(bytes.fromhex("FE FF FF EA"))  # B . (infinite loop)
