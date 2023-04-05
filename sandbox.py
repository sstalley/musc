import sys
import warnings
from RestrictedPython.PrintCollector import PrintCollector
from RestrictedPython import compile_restricted

if len(sys.argv) < 2:
    print(f"usage: {sys.argv[0]} <untrusted_script.py>")
    exit()

fileName = sys.argv[1]

with open(fileName, mode='r') as file: # b is important -> binary
    source_code = file.read()

loc = {'_print_': PrintCollector, '_getattr_': getattr}

with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    byte_code = compile_restricted(source_code, '<inline>', 'exec')
exec(byte_code, loc)
print(f"{loc['_print']()}")
