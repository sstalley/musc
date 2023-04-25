from account_info import school_suffix
import random

user_file = "usernames.csv"
out_file = "py2_values.csv"

#Pick reasonable values
ss = list(range(50,150))

outlines = ["user,email,kp,km,cp,cm,As,Ap,Bs,Bp,Ms,Mp"]
random.seed(1359)

# add some noise to make it seem more real:
kp = 0.25  + 0.1 * random.random()
km = 0.0625 + 0.01 * random.random()

with open( user_file, 'r' ) as file:
    users = file.readlines()

    for user in users:
        user = user.strip()
        us = random.choice(ss)
        up = random.choice(list(range(5,us)))

        cp = us + up
        cm = us - up

        # Mike has plenty of power
        Ms = us + 6
        Mp = up + 6

        # Al has speed but is missing acceleration
        As = us + 3
        Ap = up - 3

        # Bob is close, but needs MORE POWER
        Bs = us - 1
        Bp = up - 1

        outlines.append(f"{user}, {user}@{school_suffix}, {kp}, {km}, {cp}, {cm}, {As}, {Ap}, {Bs}, {Bp}, {Ms}, {Mp}")

outlines = "\n".join(outlines)

with open(out_file, 'w') as file:
    file.write(outlines)

