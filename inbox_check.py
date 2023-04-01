import imaplib
import email
from account_info import gmail_imap, gmail_email, gmail_password

# Credit to NeuralNine for putting together a great tutorial
# Email checking stuff adapted from:
# https://www.youtube.com/watch?v=4iMZUhkpWAc

imap = imaplib.IMAP4_SSL(gmail_imap)
imap.login(gmail_email, gmail_password)

imap.select(readonly=False)

_, n_msgs = imap.search(None, "(UNSEEN)")


for n_msg in n_msgs[0].split():
    _, data = imap.fetch(n_msg, "(RFC822)")

    message = email.message_from_bytes(data[0][1])

    print(f"From: {message.get('From')}")
    print(f"Subject: {message.get('Subject')}")

    _, data = imap.store(n_msg,'+FLAGS','\Seen')


imap.close()
