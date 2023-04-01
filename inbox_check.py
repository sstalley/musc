import imaplib
import email
import os
import re
from account_info import gmail_imap, gmail_email, gmail_password, school_suffix
from result_sender import send_result


no_assignno_str = \
"I cannot determine which assignment this is.\n" + \
"Please ensure that the assignment number is the only number in the Subject field.\n\n" + \
"Example Acceptable Subject Lines:\n" + \
"StudentName PY-0\n" + \
"Assignment for MUSC 10\n" + \
"Maybe It will work this time 3"


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


def download_attachments(message, filetype=".py", file_dir="./test_dir"):
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

           filePath = os.path.join(file_dir, fileName)
           if not os.path.isfile(filePath):
               print(f"Downloading {fileName} ...")
               fp = open(filePath, 'wb')
               fp.write(part.get_payload(decode=True))
               fp.close()



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

        student_email = message.get('From')
        if school_suffix.upper() not in student_email.upper():
            raise NotSchoolAddress

        subject = message.get('Subject')
        sub_nums = re.search("\d", subject)
        if sub_nums is None:
            raise NoAssignmentNumber

        assign_n = int(subject[sub_nums.start():sub_nums.end()])


        # download attachments to run
        download_attachments(message, file_dir="./test_dir")

        print(f"From: {student_email}")
        print(f"Subject: {subject}")

        #For testing pass everything that is valid
        send_result(student_email, assign_n, 1, 1, "Great Work!")

        _, data = imap.store(n_msg,'+FLAGS','\Seen')

    except NoAssignmentNumber:

        print(f"No assignment number!")
        send_result(student_email, "?", 0, 1, no_assignno_str)
        _mark_as_read(n_msg)

    except NotSchoolAddress:
        # don't respond, just mark as read and ignore
        print(f"Not a School Address!")
        _mark_as_read(n_msg)

imap.close()
imap.logout()
