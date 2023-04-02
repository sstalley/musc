import subprocess
import threading
import time

MAX_RUNTIME = 30

class UnknownAssignment(Exception):
    r"MUSC doesn't know how to grade that assignment yet"
    pass

class TooManyFiles(Exception):
    r"This assignment doesn't need that many source files"
    pass


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

    return runtime, stdout, stderr


def _grade_py0(source):

    score = 1 # one point for getting this far

    cmd = ['python', source]
    runtime, stdout, stderr = _run_time(cmd)

    print("Standard Output:", stdout)
    print("Standard Error:", stderr)

    #TODO: Evaluate run
    feedback = f"Great Work!\n\nStandard Output:\n{stdout}\nStandard Error:\n{stderr}"
    return score, 4, feedback


def run_grade(assign_no, path_to_source):

    if assign_no == 0:
        if len(path_to_source) != 1:
            raise TooManyFiles
        score, score_max, feedback = _grade_py0(path_to_source[0])
    else:
        raise UnknownAssignment

    return score, score_max, feedback
