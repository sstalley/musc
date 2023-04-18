import sys
import time
import re
import os
from runner_grader import MAX_RUNTIME, PY1_MAX_SCORE, test_dir
from pathlib import Path

#various semi-common voltages
voltzz = [ "1.5", "3.3", "3.7", "5.0", "7.2", "12", "24", "120"]
e12rs = [100, 120, 150, 180, 220, 270, 330, 390, 470, 560, 680, 820]


#faking suff hopefully?
def __input(prompt=None):
    if prompt is not None:
        print(prompt + "10.0\n")

    return "10.0"

def ol(v,r):
    return v/r

def r_calc(r1, r2, r3):
    return 1/(1/r1 + 1/(r2 + r3))

def vdiv(r2, r3, v):
    return r3/(r2+r3) * v

def within_tol(a, b, tol=0.05):
    for (az, bz) in zip(a, b):
        if az * (1-tol) > bz:
            return False
        if az * (1+tol) < bz:
            return False

    return True

def score_fn(fn_name, ctrl_name, fn_valuez, ctrl_valuez):

    x = y = "SETME"

    # can I call it?
    try:
        call_str = f"{fn_name}({', '.join(fn_valuez[0])})"
        print(f"calling {call_str}")
        exec(call_str)

    except NameError:
        print(f"Could not find function {fn_name}")
        return 0
    except TypeError:
        fn_type = exec(f"type({fn_name})")
        print(f"{fn_name} is a {fn_type}, not a function")
        return 0
    except Exception as e:
        print(f"calling {fn_name} threw the following exception:")
        print(e)
        print(f"Not gonna try any harder...")
        return 0

    # does it return valid values?
    for fn_i in fn_valuez:
        call_str = f"x = {fn_name}({', '.join(fn_i)})"
        loc = {}
        try:
            exec(call_str, globals(), loc)
            x = loc['x']
            int(x)
        except ValueError:
            print(f"Could not understand output {x}")
            return 1
        except Exception as e:
            print(e)
            print(f"Not gonna try any harder...")
            return 1

    for fn_i, ctrl_i in zip(fn_valuez, ctrl_valuez):
        loc = {}
        try:
            exec(f"x = {fn_name}({', '.join(fn_i)})", globals(), loc)
            exec(f"y = {ctrl_name}({', '.join(ctrl_i)})\n", globals(), loc)
            x = loc['x']
            y = loc['y']
        except Exception as e:
            print(e)
            print(f"Not gonna try any harder...")
            return 2

        if not within_tol([x], [y]):
            print(f"{x} and {y} too different")
            return 2

    return 3


if len(sys.argv) < 4:
    print(f"usage: {sys.argv[0]} <untrusted_script.py> <r1> <r2>")
    exit()

fileName = sys.argv[1]
__r1 = str(sys.argv[2])
__r2 = str(sys.argv[3])

with open(fileName, mode='r') as file:
    source_code = file.read()

# GLOBAL CHECKS (does it call input twice?)
inputs = len(re.findall("input\(", source_code))
print(f"Inputs counted: {inputs}")
score = 0
if inputs == 1:
    score = 1
if inputs == 2:
    score = 2


# Semi-Hack: go to my input:
# print(f"old source code:\n{source_code}")
source_code = re.sub("input\(", "__input(", source_code)
# print(f"new source code:\n{source_code}")


fns = ["calc_total_r", "ohms_law", "r3_voltage"]
ctrls = ["r_calc", "ol", "vdiv"]


try:
    exec(source_code)
except Exception as e:
    print(e)
    print("something bad happend when importing functions")
    print(f"MUSC TOTAL {score}")
    exit()

#Sweep resistor values and check
fn_values_1   = [[str(r)] for r in e12rs]
ctrl_values_1 = [[__r1, __r2, str(r)] for r in e12rs]
score = score + score_fn(fns[0], ctrls[0], fn_values_1, ctrl_values_1)

#fn and ctrl are the same here
ohm_values = [[v, __r1] for v in voltzz]
score = score + score_fn(fns[1], ctrls[1], ohm_values, ohm_values)

#sweep voltages and check
fn_values_3   = [[__r1, v] for v in voltzz]
ctrl_values_3 = [[__r2, __r1, v] for v in voltzz]
score = score + score_fn(fns[2], ctrls[2], fn_values_3, ctrl_values_3)

print(f"MUSC TOTAL {score}")


