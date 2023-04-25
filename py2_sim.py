import sys
import csv

MIN_TIME = 87.9 # 0UTTAT1ME

class Racer:

    def get_eff(S,P, ssppk):
        return (S*S + P*P) * ssppk

    def get_weight(S,P, spk):
        return (S*P) * spk

    def get_speed(S, sk):
        return S * sk

    def get_accel(P, pk):
        return P * pk

    def __init__(self, name, params=None, S=None, P=None):
        self.name = name
        kp = float(params["kp"])
        km = float(params["km"])
        cp = float(params["cp"])
        cm = float(params["cm"])

        ssppk = kp + km
        spk = 2 * (kp - km)
        sk = 2 * (cp * kp + cm * km)
        pk = 2 * (cp * kp - cm * km)
        self.k = kp * cp * cp + km * cm * cm + MIN_TIME

        self.eff = Racer.get_eff(S,P, ssppk)
        self.weight = Racer.get_weight(S,P, spk)
        self.speed = Racer.get_speed(S, sk)
        self.accel = Racer.get_accel(P, pk)


    def get_perf(self, prog):
        #prog = 1: (final) 50/50 S&P, SS+PP&SP
        #prog = 0: all S & P terms
        return self.k - self.speed - self.accel + prog * (self.weight + self.eff)

    def get_name(self):
        return self.name


def make_racers(params, S, P):
    racer_names = ["Tim Taylor", "Al Borland", "Mike Baxter", "Bob Vila"]

    tim = Racer(racer_names[0], params=params, S=S, P=P)

    racers = [tim]
    for i, name in enumerate(racer_names[1:]):
        comp_str = name[0]
        competitor = Racer(name, params=params,
                           S=float(params[comp_str + "s"]),
                           P=float(params[comp_str + "p"]))
        racers.append(competitor)

    return racers


def takeTime(elem):
    return elem[1]

class RaceTrack:

    def __init__(self, racers):
        self.racers = racers

    def get_race_status(self, prog=None):
        status = []
        return_time = False
        if prog is None:
            prog = 1.0
            return_time = True

        for racer in self.racers:
            name = racer.get_name()
            time = racer.get_perf(prog=prog)
            status.append((name,time))

        status.sort(key=takeTime)

        if return_time:
            report = ["FINAL RACE RESULTS:"]
        elif prog == 0:
            report = ["Standings right off the line:"]
        else:
            report = [f"Standings at {prog:.0%} point:"]

        for place, (racer, time) in enumerate(status):
            line = f"#{place+1}: {racer:<16}"
            if return_time:
                line = line + f"  {time:.3f} Seconds"
            report.append(line)
        return "\n".join(report)

    def run_race(self):
        for time in [0, 0.25, 0.5, 0.75, None]:
            print(self.get_race_status(prog=time)+"\n")




if len(sys.argv) < 5:
    print(f"usage: {sys.argv[0]} <parameters.csv> <username> <S> <P>")
    exit()

csvFileName = str(sys.argv[1])
username = str(sys.argv[2])
S = int(sys.argv[3])
P = int(sys.argv[4])

params = {}

with open(csvFileName, mode='r') as file:
    reader = csv.DictReader(file)
    found = False
    for student in reader:
        if student['user'].strip().lower() == username.strip().lower():
            found = True
            params = student
            break

    if not found:
        print(f"Error: could not find user {username} information in {csvFileName}")
        exit()

print(f"Running Race with S={S} P={P} for {username}\n")
racers = make_racers(params, S, P)
race = RaceTrack(racers)
race.run_race()

