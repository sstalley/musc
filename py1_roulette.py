from account_info import school_suffix
import random

user_file = "usernames.csv"
out_file = "py1_values.csv"

start_str = "lllluuuuccc"
mid_str = "llluuudddrrrcccccc"
fin_str = "x"
outlines = ["user,email,commands"]


random.seed(1359)

with open( user_file, 'r' ) as file:
    users = file.readlines()

    for user in users:
        user = user.strip()

        commands = ""
        for string in [start_str, mid_str, fin_str]:
            com = random.sample(string, k=len(string))
            for c in com:
                commands = commands + c

        outlines.append(f"{user}, {user}@{school_suffix}, {commands}")


outlines = "\n".join(outlines)

with open(out_file, 'w') as file:
    file.write(outlines)
