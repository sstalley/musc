import subprocess
import threading
import time
import re

MAX_RUNTIME = 300

class UnknownAssignment(Exception):
    r"MUSC doesn't know how to grade that assignment yet"
    pass

class TooManyFiles(Exception):
    r"This assignment doesn't need that many source files"
    pass


# Taken from https://stackabuse.com/python-validate-email-address-with-regular-expressions-regex/
email_regex = re.compile(r'[ \t]*([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+[ \t]*')

def _run_time(cmd):
    start_time = time.time()
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    timeout = threading.Timer(MAX_RUNTIME, proc.kill)
    try:
        timeout.start()
        stdout, stderr = proc.communicate()
    except:
        print("something bad happened...")
    finally:
        timeout.cancel()

    end_time = time.time()
    runtime = end_time - start_time

    print(f"{cmd} ran in {runtime:.3f} seconds")

    return runtime, stdout.decode().splitlines(), stderr.decode().splitlines()


def _grade_py0(source):

    score = 0

    cmd = ['python', 'sandbox.py', source]
    runtime, stdout, stderr = _run_time(cmd)

    file = open(source, 'r')
    flines = file.readlines()


    print("Standard Output:", stdout)
    print("Standard Error:", stderr)

    feedback = f"{source} contents:\n"
    for line in flines:
        feedback = feedback + line

    feedback = feedback + f"{source} ran in {runtime:.3f} seconds\n\nProgram Output:\n"

    for line in stdout:
        feedback = feedback + line + "\n"

    feedback = feedback + "\nError Output:\n"
    for line in stderr:
        feedback = feedback + line + "\n"


    score = score + 1# one point for getting this far
    feedback = feedback + "\nGrading:\nSubmitted valid .py file (+1)\n"

    if len(flines) <= 1:
        score = score + 1
        feedback = feedback + "Extra Credit: One-line bonus (+1)\n"

    if len(stderr) < 1:
        score = score + 1
        feedback = feedback + ".py file runs without errors (+1)\n"

    total = 0
    for i, line in enumerate(stdout):
        print(f"Output Line {i}: {line}")
        if i == 0:
            if re.fullmatch(email_regex, line):
                score = score + 1
                feedback = feedback + f"\n{line} is a valid email address (+1)"
            else:
                feedback = feedback + f"\n{line} is a not a valid email address (0)"

        elif i == 1:
            digits = re.findall("\d", line)
            n_d = 0
            for d in digits:
                n_d = n_d + 1
                total = total + int(d)

            if n_d > 8:
                score = score + 1
                feedback = feedback + f"\nvalid ID number (+1)"
            else:
                feedback = feedback + f"\nOnly found {n_d} digits of ID (0)"

        elif i == 2:
            if int(line) == total:
                score = score + 1
                feedback = feedback + f"\nSum correct ({int(line)} == {total}) (+1)"
            else:
                feedback = feedback + f"\nSum not correct ({int(line)} != {total}) (0)"

    return score, 5, feedback


def run_grade(assign_no, path_to_source):

    if assign_no == 0:
        if len(path_to_source) != 1:
            raise TooManyFiles
        score, score_max, feedback = _grade_py0(path_to_source[0])
    else:
        raise UnknownAssignment

    return score, score_max, feedback
