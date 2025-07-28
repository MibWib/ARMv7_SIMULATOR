# Simple, robust test generator for ARM cache hierarchy testing

def generate_working_memory_test():
    """Generate a memory test that actually works with ARM encoding"""
    
    print("Generating working_memory_test.bin...")
    with open("working_memory_test.bin", "wb") as f:
        # Initialize base address - use simple immediate that works
        f.write(bytes.fromhex("00 1A A0 E3"))  # MOV R1, #0x1000 (using 8-bit immediate)
        
        # Initialize some data values
        f.write(bytes.fromhex("11 20 A0 E3"))  # MOV R2, #0x11
        f.write(bytes.fromhex("22 30 A0 E3"))  # MOV R3, #0x22
        f.write(bytes.fromhex("33 40 A0 E3"))  # MOV R4, #0x33
        f.write(bytes.fromhex("44 50 A0 E3"))  # MOV R5, #0x44
        
        # Sequential stores - should cause cache misses initially
        f.write(bytes.fromhex("00 20 81 E5"))  # STR R2, [R1, #0]
        f.write(bytes.fromhex("04 30 81 E5"))  # STR R3, [R1, #4]
        f.write(bytes.fromhex("08 40 81 E5"))  # STR R4, [R1, #8]
        f.write(bytes.fromhex("0C 50 81 E5"))  # STR R5, [R1, #12]
        
        # Sequential loads - should hit cache if data is in same block
        f.write(bytes.fromhex("00 60 91 E5"))  # LDR R6, [R1, #0]
        f.write(bytes.fromhex("04 70 91 E5"))  # LDR R7, [R1, #4]
        f.write(bytes.fromhex("08 80 91 E5"))  # LDR R8, [R1, #8]
        f.write(bytes.fromhex("0C 90 91 E5"))  # LDR R9, [R1, #12]
        
        # More stores to fill cache and cause potential conflicts
        f.write(bytes.fromhex("10 20 81 E5"))  # STR R2, [R1, #16]
        f.write(bytes.fromhex("14 30 81 E5"))  # STR R3, [R1, #20]
        f.write(bytes.fromhex("18 40 81 E5"))  # STR R4, [R1, #24]
        f.write(bytes.fromhex("1C 50 81 E5"))  # STR R5, [R1, #28]
        
        # Load back - test cache behavior
        f.write(bytes.fromhex("10 A0 91 E5"))  # LDR R10, [R1, #16]
        f.write(bytes.fromhex("14 B0 91 E5"))  # LDR R11, [R1, #20]
        
        # Test different cache lines
        f.write(bytes.fromhex("20 20 81 E5"))  # STR R2, [R1, #32]
        f.write(bytes.fromhex("30 30 81 E5"))  # STR R3, [R1, #48]
        f.write(bytes.fromhex("40 40 81 E5"))  # STR R4, [R1, #64]
        
        # Load from different lines
        f.write(bytes.fromhex("20 C0 91 E5"))  # LDR R12, [R1, #32]
        f.write(bytes.fromhex("30 D0 91 E5"))  # LDR R13, [R1, #48]
        f.write(bytes.fromhex("40 E0 91 E5"))  # LDR R14, [R1, #64]
        
        # Go back to original addresses to test cache retention
        f.write(bytes.fromhex("00 10 91 E5"))  # LDR R1, [R1, #0] (reload first value)
    
    print("Generated working_memory_test.bin with 25 instructions")

def generate_simple_arithmetic_test():
    """Generate a simple arithmetic test for comparison"""
    
    print("Generating simple_arithmetic_test.bin...")
    with open("simple_arithmetic_test.bin", "wb") as f:
        # Initialize registers
        f.write(bytes.fromhex("01 10 A0 E3"))  # MOV R1, #1
        f.write(bytes.fromhex("02 20 A0 E3"))  # MOV R2, #2
        f.write(bytes.fromhex("03 30 A0 E3"))  # MOV R3, #3
        f.write(bytes.fromhex("04 40 A0 E3"))  # MOV R4, #4
        
        # Arithmetic operations
        f.write(bytes.fromhex("02 50 81 E0"))  # ADD R5, R1, R2
        f.write(bytes.fromhex("03 60 82 E0"))  # ADD R6, R2, R3
        f.write(bytes.fromhex("04 70 83 E0"))  # ADD R7, R3, R4
        f.write(bytes.fromhex("06 80 85 E0"))  # ADD R8, R5, R6
        f.write(bytes.fromhex("07 90 88 E0"))  # ADD R9, R8, R7
        
        # Subtraction
        f.write(bytes.fromhex("01 A0 49 E0"))  # SUB R10, R9, R1
        f.write(bytes.fromhex("02 B0 4A E0"))  # SUB R11, R10, R2
        
        # Logical operations
        f.write(bytes.fromhex("0B C0 8A E1"))  # ORR R12, R10, R11
        f.write(bytes.fromhex("0C D0 2B E0"))  # EOR R13, R11, R12
        
        # Minimal memory operations at the end
        f.write(bytes.fromhex("00 1A A0 E3"))  # MOV R1, #0x1000
        f.write(bytes.fromhex("00 D0 81 E5"))  # STR R13, [R1, #0]
        f.write(bytes.fromhex("00 E0 91 E5"))  # LDR R14, [R1, #0]
    
    print("Generated simple_arithmetic_test.bin with minimal memory usage")

def generate_cache_test():
    """Generate a test specifically for cache behavior differences"""
    
    print("Generating cache_behavior_test.bin...")
    with open("cache_behavior_test.bin", "wb") as f:
        # Base address
        f.write(bytes.fromhex("00 1A A0 E3"))  # MOV R1, #0x1000
        
        # Different data patterns
        f.write(bytes.fromhex("AA 20 A0 E3"))  # MOV R2, #0xAA
        f.write(bytes.fromhex("BB 30 A0 E3"))  # MOV R3, #0xBB
        f.write(bytes.fromhex("CC 40 A0 E3"))  # MOV R4, #0xCC
        
        # Pattern that tests block size differences
        # Store to address 0
        f.write(bytes.fromhex("00 20 81 E5"))  # STR R2, [R1, #0]
        
        # Load from nearby addresses - hits depend on block size
        f.write(bytes.fromhex("04 50 91 E5"))  # LDR R5, [R1, #4]   - hit if block >= 8 bytes
        f.write(bytes.fromhex("08 60 91 E5"))  # LDR R6, [R1, #8]   - hit if block >= 12 bytes
        f.write(bytes.fromhex("0C 70 91 E5"))  # LDR R7, [R1, #12]  - hit if block >= 16 bytes
        f.write(bytes.fromhex("10 80 91 E5"))  # LDR R8, [R1, #16]  - hit if block >= 20 bytes
        f.write(bytes.fromhex("14 90 91 E5"))  # LDR R9, [R1, #20]  - hit if block >= 24 bytes
        f.write(bytes.fromhex("18 A0 91 E5"))  # LDR R10, [R1, #24] - hit if block >= 28 bytes
        f.write(bytes.fromhex("1C B0 91 E5"))  # LDR R11, [R1, #28] - hit if block >= 32 bytes
        
        # Access pattern for associativity testing
        # Store to potentially conflicting addresses
        f.write(bytes.fromhex("00 30 81 E5"))  # STR R3, [R1, #0]   (overwrite)
        f.write(bytes.fromhex("20 40 81 E5"))  # STR R4, [R1, #32]  (might conflict depending on cache size)
        
        # Try to load original data
        f.write(bytes.fromhex("00 C0 91 E5"))  # LDR R12, [R1, #0]  (should get R3's value)
        f.write(bytes.fromhex("20 D0 91 E5"))  # LDR R13, [R1, #32] (should get R4's value)
        
        # Test cache retention
        f.write(bytes.fromhex("04 E0 91 E5"))  # LDR R14, [R1, #4]  (hit/miss depends on cache state)
    
    print("Generated cache_behavior_test.bin for cache analysis")

def main():
    print("Generating fixed test files for ARM cache hierarchy simulation...\n")
    
    generate_working_memory_test()
    print()
    generate_simple_arithmetic_test() 
    print()
    generate_cache_test()
    
    print(f"\nGenerated files:")
    print("- working_memory_test.bin      : Memory-intensive operations")
    print("- simple_arithmetic_test.bin   : Arithmetic-heavy operations")  
    print("- cache_behavior_test.bin      : Cache behavior testing")
    print(f"\nTo test:")
    print("python main.py working_memory_test.bin")
    print("python main.py working_memory_test.bin --experiments")

if __name__ == "__main__":
    main()