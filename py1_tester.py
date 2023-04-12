import sys
import time
import re
import os
from runner_grader import MAX_RUNTIME, PY1_MAX_SCORE, test_dir
from py1_roulette import e12rs
from pathlib import Path

inputzz = ["10.0", "10.0", "", "", ""]
#various semi-common voltages
voltzz = [ "1.5", "3.3", "3.7", "5.0", "7.2", "12", "24", "120"]


#faking suff hopefully?
def input():
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
        exec(f"{fn_name}({', '.join(fn_valuez[0])})\n")
    except NameError:
        print(f"Could not find function {fn_name}")
        return 0

    # does it return valid values?
    for fn_i in fn_valuez:
        exec(f"x = {fn_name}({', '.join(fn_i)})\nprint(x)\n")
        print(x)
        try:
            int(x)
        except ValueError:
            print(f"Could not understand output {x}")
            return 1

    for fn_i, ctrl_i in zip(fn_valuez, ctrl_valuez):
        exec(f"x = {fn_name}({', '.join(fn_i)})\n")
        exec(f"y = {ctrl_name}({', '.join(ctrl_i)})\n")
        if not within_tol(x, y):
            print(f"{x} and {y} too different")
            return 2

    return 3


if len(sys.argv) < 2:
    print(f"usage: {sys.argv[0]} <untrusted_script.py>")
    exit()

fileName = sys.argv[1]

with open(fileName, mode='r') as file: # b is important -> binary
    source_code = file.read()


# GLOBAL CHECKS (does it call input twice?)
inputs = len(re.findall("input\(", source_code))
print(f"Inputs counted: {inputs}")
score = 0
if inputs == 1:
    score = 1
if inputs == 2:
    score = 2


fns = ["calc_total_r", "ohms_law", "r3_voltage"]
ctrls = ["r_calc", "ol", "vdiv"]


for fn in fns:
    try:
        #TODO: un-hard-code
        exec(f"from test_dir.{Path(fileName).stem} import {fn}")
    except Exception as e:
        print(e)
        print("something bad happend when importing functions")


#TODO: actually lookup correct resistance values
# For now just use fixed values for sstalley
r1 = "100"
r2 = "120"

#Sweep resistor values and check
fn_values_1   = [[str(r)] for r in e12rs]
ctrl_values_1 = [[r1, r2, str(r)] for r in e12rs]
score = score + score_fn(fns[0], ctrls[0], fn_values_1, ctrl_values_1)

#fn and ctrl are the same here
ohm_values = [[v, r1] for v in voltzz]
score = score + score_fn(fns[1], ctrls[1], ohm_values, ohm_values)

#sweep voltages and check
fn_values_3   = [[r1, v] for v in voltzz]
ctrl_values_3 = [[r1, r1, v] for v in voltzz]
score = score + score_fn(fns[2], ctrls[2], fn_values_3, ctrl_values_3)

print(f"MUSC TOTAL {score}")


