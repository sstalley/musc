import subprocess
import threading
import time
import re
import csv

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

class ValuesNotFound(Exception):
    r"Could Not Find Student-specific Values"
    pass

# Taken from https://stackabuse.com/python-validate-email-address-with-regular-expressions-regex/
email_regex = re.compile(r'[ \t]*([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+[ \t]*')
#TODO: refactor to just no whitespace version
email_regex_nows = re.compile(r'([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+')

PY1_MAX_SCORE = 10
py1_values_file = "py1_values.csv"

PY2_MAX_SCORE = 10
py2_values = "py2_values.csv"

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


def _py2_get_vals(email_body):

    print("PY2 - getting values")

    print(email_body)
    try:
        email_body = str(email_body)
        print(email_body)
        s_str = re.findall(r'\d+[sS]', email_body)[0]
        p_str = re.findall(r'\d+[pP]', email_body)[0]
        s = int(s_str[:-1])
        p = int(p_str[:-1])

    except Exception as e:
        print("Exception raised while looking for S & P values:", e)
        raise ValuesNotFound

    return s, p

def _py1_get_rs(student_email):
    with open( py1_values_file, 'r' ) as the_file:
        reader = csv.DictReader(the_file)

        for student in reader:
            print(f"comparing:{student['email'].lower()} and {student_email.lower()}")
            if student_email.lower().find(student['user'].lower()+"@") != -1:
                return str(student['r1']), str(student['r2'])

    raise ValuesNotFound


def _grade_pre_graded_result(stdout, score, max_score):
    for i, line in enumerate(stdout):
        print(f"Output Line {i}: {line}")

    feedback = f"Score: {score} out of {max_score} (error running code)\n"
    # mostly copy what the py1 sandbox already figured out
    for line in reversed(stdout):
        if re.search("MUSC TOTAL", line) is None:
            continue

        score = score + int(re.search("\\d+", line).group())

        feedback = f"Score: {score} out of {max_score}\n"

    return score, feedback

def _grade_py2(stdout, score):
    return _grade_pre_graded_result(stdout, score, PY2_MAX_SCORE)

def _grade_py1(stdout, score):
    return _grade_pre_graded_result(stdout, score, PY1_MAX_SCORE)

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


def run_grade(assign_no, path_to_source, student_email, email_body):

    score = 0

    if assign_no == 0:
        if len(path_to_source) < 1:
            raise NoSourceFile
        if len(path_to_source) != 1:
            raise TooManyFiles
        source = path_to_source[0]
        cmd = ['python', source]
        score_max = 5
    elif assign_no == 1:
        if len(path_to_source) < 1:
            raise NoSourceFile
        if len(path_to_source) != 1:
            raise TooManyFiles
        source = path_to_source[0]
        r1, r2 = _py1_get_rs(student_email)
        cmd = ['python', 'py1_tester.py', source, r1, r2]
        score_max = 10

    elif assign_no == 2:
        score = 1
        S, P = _py2_get_vals(email_body)
        score = score + 1
        username = re.findall("[a-zA-Z0-9]+@", student_email)[0][:-1]
        source = None
        print(f"Username:{username}")
        cmd = ['python', 'py2_sim.py', py2_values, username, str(S), str(P)]
        score_max = 10

    elif assign_no < 6:
        raise UnimplementedAssignment

    else:
        raise UnknownAssignment

    runtime, stdout, stderr = _run_time(cmd)

    print("Standard Output:", stdout)
    print("Standard Error:", stderr)

    if source is not None:
        file = open(source, 'r')
        flines = file.readlines()

        feedback = [f"{source} contents:\n"]
        for line in flines:
            feedback.append(line)

        feedback.append(f"{source} ran in {runtime:.3f} seconds\n\nProgram Output:\n")
    else:
        feedback = [f"Ran in {runtime:.3f} seconds\n\nProgram Output:\n"]

    for line in stdout:
        feedback.append(line + "\n")

    feedback.append("\nError Output:\n")
    for line in stderr:
        feedback.append(line + "\n")

    if source is not None:
        score = score + 1# one point for getting this far
        feedback.append("\nGrading:\nSubmitted valid .py file (+1)\n")

        if len(stderr) < 1:
            score = score + 1
            feedback.append(".py file runs without errors (+1)\n")

    if assign_no == 0:
        assign_score, assign_feedback = _grade_py0(flines, stdout)
        score = score + assign_score
    elif assign_no == 1:
        score, assign_feedback = _grade_py1(stdout, score)
    elif assign_no == 2:
        score, assign_feedback = _grade_py2(stdout, 0) #set grade to 0 as workaround here
    elif assign_no < 6:
        raise UnimplementedAssignment
    else:
        raise UnknownAssignment

    for line in assign_feedback:
        feedback.append(line)


    return score, score_max, "".join(feedback)
