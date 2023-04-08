import smtplib

from account_info import gmail_smtp, gmail_smtp_port, gmail_email, gmail_password
from email.mime.text import MIMEText
from result_sender import tail_str
import csv

def make_body(prompt, student, footer):
    body = prompt
    body.append(f"R Values for {student['email']}:\n")
    body.append(f"--------------------------------\n")
    body.append(f"R1: {int(student['r1'])} Ohms\n")
    body.append(f"R2: {int(student['r2'])} Ohms\n")
    body.append(f"\n\n")
    body.append(footer)
    body = "".join(body)
    print(body)
    return body


spam_list = r"./test_list.csv"
prompt_file = "./py1_prompt.txt"


with open( spam_list, 'r' ) as the_file:
    reader = csv.DictReader(the_file)

    subject = "PY-1 Assignment: Electrical Functions"

    smtp_server = smtplib.SMTP_SSL(gmail_smtp, gmail_smtp_port)
    smtp_server.login(gmail_email, gmail_password)

    for student in reader:
        #Kinda hacky - should probably only open this once, but oh well
        with open( prompt_file, 'r', encoding="utf-8") as the_file:
            prompt = the_file.readlines()
            body = make_body(prompt, student, tail_str)
            msg = MIMEText(body)
            msg['Subject'] = subject
            msg['From'] = gmail_email
            msg['To'] = student['email']
            #smtp_server.sendmail(gmail_email, [student['email']], msg.as_string())

    smtp_server.quit()
