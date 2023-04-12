import subprocess
import threading
import time
import re

MAX_RUNTIME = 30
test_dir = "./test_dir/"


class UnimplementedAssignment(Exception):
    r"MUSC can't grade that assignment yet"
    pass

class UnknownAssignment(Exception):
    r"MUSC doesn't know how to grade that assignment yet"
    pass

class TooManyFiles(Exception):
    r"This assignment doesn't need that many source files"
    pass


# Taken from https://stackabuse.com/python-validate-email-address-with-regular-expressions-regex/
email_regex = re.compile(r'[ \t]*([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+[ \t]*')

PY1_MAX_SCORE = 10

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

def _grade_py1(flines, stdout):

    for i, line in enumerate(stdout):
        print(f"Output Line {i}: {line}")

    # mostly copy what the py1 sandbox already figured out
    for line in reverse(stdout):
        if re.search("MUSC TOTAL", line) is None:
            continue

        score = int(re.search("\\d+", line).group())

        feedback = f"Score: {score} out of {PY1_MAX_SCORE}\n"

    return score, feedback

def _grade_py0(flines, stdout):

    score = 0
    feedback = []

    if len(flines) <= 1:
        score = score + 1
        feedback.append("Extra Credit: One-line bonus (+1)\n")

    total = 0
    for i, line in enumerate(stdout):
        print(f"Output Line {i}: {line}")
        if i == 0:
            if re.fullmatch(email_regex, line):
                score = score + 1
                feedback.append(f"{line} is a valid email address (+1)\n")
            else:
                feedback.append(f"{line} is a not a valid email address (0)\n")

        elif i == 1:
            digits = re.findall("\d", line)
            n_d = 0
            for d in digits:
                n_d = n_d + 1
                total = total + int(d)

            if n_d > 8:
                score = score + 1
                feedback.append(f"valid ID number (+1)\n")
            else:
                feedback.append(f"Only found {n_d} digits of ID (0)\n")

        elif i == 2:
            try:
                sum_val = int(line)
            except ValueError:
                sum_val = -1

            if sum_val == total:
                score = score + 1
                feedback.append(f"Sum correct ({int(line)} == {total}) (+1)\n")
            elif sum_val == -1:
                feedback.append(f"Sum could not be found (0)\n")
            else:
                feedback.append(f"Sum not correct ({int(line)} != {total}) (0)\n")

    return score, feedback


def run_grade(assign_no, path_to_source):

    score = 0

    if assign_no == 0:
        if len(path_to_source) != 1:
            raise TooManyFiles
        source = path_to_source[0]
        cmd = ['python', source]
        score_max = 5
    elif assign_no == 1:
        if len(path_to_source) != 1:
            raise TooManyFiles
        source = path_to_source[0]
        cmd = ['python', 'py1_tester.py', source]
        score_max = 10

    elif assign_no < 6:
        raise UnimplementedAssignment

    else:
        raise UnknownAssignment

    runtime, stdout, stderr = _run_time(cmd)

    file = open(source, 'r')
    flines = file.readlines()

    print("Standard Output:", stdout)
    print("Standard Error:", stderr)

    feedback = [f"{source} contents:\n"]
    for line in flines:
        feedback.append(line)

    feedback.append(f"{source} ran in {runtime:.3f} seconds\n\nProgram Output:\n")

    for line in stdout:
        feedback.append(line + "\n")

    feedback.append("\nError Output:\n")
    for line in stderr:
        feedback.append(line + "\n")


    score = score + 1# one point for getting this far
    feedback.append("\nGrading:\nSubmitted valid .py file (+1)\n")

    if len(stderr) < 1:
        score = score + 1
        feedback.append(".py file runs without errors (+1)\n")

    if assign_no == 0:
        assign_score, assign_feedback = _grade_py0(flines, stdout)
    elif assign_no == 1:
        assign_score, assign_feedback = _grade_py1(flines, stdout)
    elif assign_no < 6:
        raise UnimplementedAssignment
    else:
        raise UnknownAssignment


    score = score + assign_score
    for line in assign_feedback:
        feedback.append(line)


    return score, score_max, "".join(feedback)
