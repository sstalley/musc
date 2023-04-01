import imaplib
import email
from account_info import imap_server, imap_email, imap_password

# Credit to NeuralNine for putting together a great tutorial
# Email checking stuff adapted from:
# https://www.youtube.com/watch?v=4iMZUhkpWAc

imap = imaplib.IMAP4_SSL(imap_server)
imap.login(imap_email, imap_password)

imap.select("Inbox")

_, n_msgs = imap.search(None, "ALL")


for n_msg in n_msgs[0].split():
    _, data = imap.fetch(msgnum, "(RFC822)")

    message = email.message_from_bytes(data[0][1])

    print(f"Message # {n_msg}")
    print(f"From: {message.get('From')}")
    print(f"Subject: {message.get('Subject')}")
