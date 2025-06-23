"""
-------------------------------------------------------
[program description]
-------------------------------------------------------
Author:  Kieran Mochrie
ID:      169048254
Email:   moch8254@mylaurier.ca
__updated__ = "2025-06-23"
-------------------------------------------------------
"""
# Imports

# Constants

# file_reader.py

from memory import write_word


def load_binary(filename, x):
    try:
        with open(filename, "rb") as file:
            address = 0
            while True:
                buffer = file.read(4)
                if len(buffer) < 4:
                    print('break')

                    break  # Stop if fewer than 4 bytes are read (end of file)

                word = (buffer[0] << 24) | (buffer[1] << 16) | (
                    buffer[2] << 8) | buffer[3]
                write_word(address, word)
                address += 4

        return x
    except IOError as e:
        print(f"Error opening binary file: {e}")
        return -1
