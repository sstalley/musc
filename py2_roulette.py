from account_info import school_suffix
import random

user_file = "usernames.csv"
out_file = "py2_values.csv"

kp = 0.25
km = 0.0625


#Pick reasonable values
ss = list(range(30,150))
ps = list(range(50,250))

outlines = ["user,email,kp,km,cp,cm"]
random.seed(1359)

with open( user_file, 'r' ) as file:
    users = file.readlines()

    for user in users:
        user = user.strip()
        us = random.sample(ss)
        up = random.sample(ps)
        outlines.append(f"{user}, {user}@{school_suffix}, {kp}, {km}, {us+up}, {us-up}")

outlines = "\n".join(outlines)

with open(out_file, 'w') as file:
    file.write(outlines)

