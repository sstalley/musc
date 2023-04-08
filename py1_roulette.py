from account_info import school_suffix
import random

user_file = "usernames.csv"
out_file = "py1_values.csv"

e12rs = [100, 120, 150, 180, 220, 270, 330, 390, 470, 560, 680, 820]
outlines = ["user,email,r1,r2"]

random.seed(1359)

with open( user_file, 'r' ) as file:
    users = file.readlines()

    for user in users:
        user = user.strip()
        rs = random.sample(e12rs, k=2)
        outlines.append(f"{user}, {user}@{school_suffix}, {rs[0]}, {rs[1]}")


outlines = "\n".join(outlines)

with open(out_file, 'w') as file:
    file.write(outlines)
