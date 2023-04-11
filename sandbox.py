import sys

if len(sys.argv) < 2:
    print(f"usage: {sys.argv[0]} <untrusted_script.py>")
    exit()

fileName = sys.argv[1]

with open(fileName, mode='r') as file: # b is important -> binary
    source_code = file.read()

byte_code = None
print(f"source code:{source_code}")
exec(source_code)
