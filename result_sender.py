import smtplib
from account_info import gmail_smtp, gmail_smtp_port, gmail_email, gmail_password
from email.mime.text import MIMEText


# MIME stuff adapted from:
# https://mailtrap.io/blog/python-send-email-gmail/


def _write_subject(assignment, score, max_score):

    subject = f"PY-{assignment} Results: "
    if score >= max_score:
        subject = subject + '\u2713 '

    return subject + f"{score}/{max_score}"


def send_result(to_email, in_reply_to, assignment, score, max_score, feedback):

    recipients = [to_email]
    subject = _write_subject(assignment, score, max_score)
    body = feedback
    thread_id = None # HACK - will this still work?

    msg = MIMEText(body)
    msg.add_header('References', in_reply_to)
    msg.add_header('In-Reply-To', in_reply_to)
    msg['Subject'] = subject
    msg['From'] = gmail_email
    msg['To'] = ', '.join(recipients)
    smtp_server = smtplib.SMTP_SSL(gmail_smtp, gmail_smtp_port)
    smtp_server.login(gmail_email, gmail_password)
    smtp_server.sendmail(gmail_email, recipients, msg.as_string())
    smtp_server.quit()
