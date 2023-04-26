import smtplib

from account_info import gmail_smtp, gmail_smtp_port, gmail_email, gmail_password
from email.mime.text import MIMEText
from result_sender import tail_str
import csv

def make_body(prompt, student, footer):
    body = prompt

    kp = float(student['kp'])
    km = float(student['km'])
    cp = float(student['cp'])
    cm = float(student['cm'])

    k_eff = kp + km
    k_weight = 2 * (kp - km)
    k_s = 2 * (cp * kp + cm * km)
    k_p = 2 * (cp * kp - cm * km)

    body.append(f"k_s:      {k_s:5.6f}\n")
    body.append(f"k_p:      {k_p:5.6f}\n")
    body.append(f"k_weight: {k_weight:5.6f}\n")
    body.append(f"k_eff:    {k_eff:5.6f}\n")
    body.append(f"\n\n")
    body.append(footer)
    body = "".join(body)
    print(body)

    body = "<br />".join(body.split("\n"))

    body = '<font face="Courier New, Courier, monospace"><pre>' + body + '</pre></font>'

    return body


spam_list = r"./py2_test.csv"
prompt_file = "./py2_prompt.txt"

with open( spam_list, 'r' ) as the_file:
    reader = csv.DictReader(the_file)

    print(f"opened {spam_list}")
    print(f"reader:{reader}")
    subject = "PY-2 Assignment: A Day at the Races"

    smtp_server = smtplib.SMTP_SSL(gmail_smtp, gmail_smtp_port)
    smtp_server.login(gmail_email, gmail_password)

    for student in reader:
        print(f"sending to {student['email']}")
        #Kinda hacky - should probably only open this once, but oh well
        with open( prompt_file, 'r', encoding="utf-8") as the_file:
            prompt = the_file.readlines()
            body = make_body(prompt, student, tail_str)
            msg = MIMEText(body, 'html')
            msg['Subject'] = subject
            msg['From'] = gmail_email
            msg['To'] = student['email']
            smtp_server.sendmail(gmail_email, [student['email']], msg.as_string())

    smtp_server.quit()
