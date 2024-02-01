import imaplib
import email
import os
import re
import subprocess
from account_info import gmail_imap, gmail_email, gmail_password, school_suffix
from result_sender import send_result
from runner_grader import run_grade, UnknownAssignment, TooManyFiles, test_dir, UnimplementedAssignment, ValuesNotFound, NoSourceFile

unimplemented_assign_str = \
"I don't know how to grade this assignment yet.\n" + \
"Hopefully your instructor finishes the software soon so you can get feedback.\n"

unknown_assign_str = \
"I don't know how to grade this assignment.\n" + \
"Please ensure that the assignment number is correct and the only number in the Subject field.\n\n" + \
"Example Acceptable Subject Lines:\n" + \
"StudentName PY-0\n" + \
"Assignment for MUSC 10\n" + \
"Maybe It will work this time 3"

no_assignno_str = \
"I cannot determine which assignment this is.\n" + \
"Please ensure that the assignment number is the only number in the Subject field.\n\n" + \
"Example Acceptable Subject Lines:\n" + \
"StudentName PY-0\n" + \
"Assignment for MUSC 10\n" + \
"Maybe It will work this time 3"

no_code_str = \
"I couldn't find any attached source files.\n" + \
"Please ensure that the source code is attached with the right file extension (ex: work.py)."

too_many_files_str = \
"That's too many files for this assignment.\n" + \
"Please ensure that the correct number of source code files are attached with the right file extension (ex: work.py)."

no_values_str = \
"I couldn't find the student-specific values for this email.\n" + \
"This is most likely a clerical bug that the instructor needs to fix.\n" + \
"please email them and bug them about this error."


class NoAssignmentNumber(Exception):
    "Raised when we can't figure out what assignment the email is about"
    pass

class NotSchoolAddress(Exception):
    "Raised when the email isn't from a school address"
    pass


def _mark_as_read(n_msg):
    _, _ = imap.store(n_msg,'+FLAGS','\Seen')


# This function adapted from:
# https://gist.github.com/kngeno/5337e543eb72174a6ac95e028b3b6456

def cleanup_directory(filetype=".py", file_dir=test_dir):
    try:
        subprocess.call(["rm",  os.path.join(file_dir, "*" + filetype), "-f"])
    except FileNotFoundError:
        print("TODO SOS: fix this error")
        pass

def download_attachments(message, filetype=".py", file_dir=test_dir):
    files = []
    for part in message.walk():
       if part.get_content_maintype() == 'multipart':
           print("skipping multi-part...")
           #print(part.as_string())
           continue
       if part.get('Content-Disposition') is None:
           print("skipping no Content-Disposition...")
           #print(part.as_string())
           continue
       fileName = part.get_filename()
       print('file names processed ...')
       if bool(fileName):
           if not fileName.upper().endswith(filetype.upper()):
               print(f"skipping {fileName} (not a {filetype} file)")
               continue

           print(f'fileName:{fileName}')
           if filetype==".py":
               filePath = os.path.join(file_dir, "source.py")
           else:
               filePath = os.path.join(file_dir, fileName)
           print(f"Downloading {fileName} ...")
           fp = open(filePath, 'wb')
           fp.write(part.get_payload(decode=True))
           fp.close()
           files.append(filePath)

    return files

# Credit to NeuralNine for putting together a great tutorial
# Email checking stuff adapted from:
# https://www.youtube.com/watch?v=4iMZUhkpWAc

imap = imaplib.IMAP4_SSL(gmail_imap)
imap.login(gmail_email, gmail_password)

imap.select(readonly=False)

_, n_msgs = imap.search(None, "(UNSEEN)")

for n_msg in n_msgs[0].split():
    _, data = imap.fetch(n_msg, "(RFC822)")

    try:

        message = email.message_from_bytes(data[0][1])
        message_id = message.get('Message-ID')

        student_email = message.get('From')
        if school_suffix.upper() not in student_email.upper():
            raise NotSchoolAddress

        subject = message.get('Subject')
        sub_nums = re.search("\d", subject)
        if sub_nums is None:
            raise NoAssignmentNumber

        body = ""

        if message.is_multipart():
            for part in message.walk():
                ctype = part.get_content_type()
                cdispo = str(part.get('Content-Disposition'))

                # skip any text/plain (txt) attachments
                if ctype == 'text/plain' and 'attachment' not in cdispo:
                    body = part.get_payload(decode=True)  # decode
                    break
        # not multipart - i.e. plain text, no attachments, keeping fingers crossed
        else:
            body = message.get_payload(decode=True)

        assign_n = int(subject[sub_nums.start():sub_nums.end()])

        # download attachments to run
        path_to_source = download_attachments(message, file_dir="./test_dir")
        path_for_npy=False
        # Kinda hacky - try to get npy files if no py files
        if len(path_to_source) < 1:
            path_for_npy=True
            path_to_source = download_attachments(message, filetype=".npy", file_dir="./test_dir")

        # grade the submission
        score, max_score, feedback = run_grade(assign_n, path_to_source, student_email, body)

        #For testing pass everything that is valid

        send_result(student_email, message_id, assign_n, score, max_score, feedback)

        # get rid of the evidence :P
        try:
            if len(path_to_source) > 0:
                if path_for_npy:
                    cleanup_directory(filetype=".npy")
                else:
                    cleanup_directory()
        except:
            pass

        _, data = imap.store(n_msg,'+FLAGS','\Seen')

    except UnimplementedAssignment:
        print(f"Unimplemented assignment number!")
        send_result(student_email, message_id, assign_n, 0, 1, unimplemented_assign_str)

    except UnknownAssignment:
        print(f"Unknown assignment number!")
        send_result(student_email, message_id, assign_n, 0, 1, unknown_assign_str)

    except NoSourceFile:
        print(f"No source code!")
        send_result(student_email, message_id, assign_n, 0, 1, no_code_str)

    except TooManyFiles:
        print(f"Too many Files!")
        send_result(student_email, message_id, assign_n, 0, 1, too_many_files_str)

    except ValuesNotFound:
        print(f"couldn't find student-specific values!")
        send_result(student_email, message_id, assign_n, 0, 1, no_values_str)

    except NoAssignmentNumber:
        print(f"No assignment number!")
        send_result(student_email, message_id, "?", 0, 1, no_assignno_str)

    except NotSchoolAddress:
        # don't respond, just mark as read and ignore
        print(f"Not a School Address!")
        _mark_as_read(n_msg)


imap.close()
imap.logout()
