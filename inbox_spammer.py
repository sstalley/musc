from datetime import datetime
import time
import subprocess
import threading

#Kinda hacky:
from runner_grader import _run_time

while True:

    tstamp = datetime.now().strftime(r"%Y%m%d_%H%M%S")
    print(f"{tstamp}: Checking Inbox")
    _, stdout, stderr = _run_time(["python", "inbox_check.py"])

    if len(stdout) > 0:
        print(f"{tstamp}: Writing Output")
        f = open( "./logs/" + tstamp + "_out.log", "a")
        f.writelines(line + '\n' for line in stdout)
        f.close()

    if len(stderr) > 0:
        print(f"{tstamp}: Writing Errors")
        f = open( "./logs/" + tstamp + "_err.log", "a")
        f.writelines(line + '\n' for line in stderr)
        f.close()

    time.sleep(30)
