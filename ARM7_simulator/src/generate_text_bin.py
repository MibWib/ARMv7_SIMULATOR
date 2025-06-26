with open("test_custom.bin", "wb") as f:
    f.write(bytes.fromhex("E3A00001"))  # MOV R0, #1
    f.write(bytes.fromhex("E2801002"))  # ADD R1, R0, #2
    f.write(bytes.fromhex("EAFFFFFE"))  # B . (infinite loop)
