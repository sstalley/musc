import sys
import csv
import numpy as np

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
    racer_names = [f"Tim Taylor ({params['user'].upper()})", "Al Borland", "Mike Baxter", "Bob Vila"]

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
        else:
            prog = np.sqrt(np.sqrt(prog)) # hack to have stuff happen earlier on in the race

        for racer in self.racers:
            name = racer.get_name()
            time = racer.get_perf(prog=prog)
            status.append((name,time))

        status.sort(key=takeTime)
        report = []
        for place, (racer, time) in enumerate(status):
            line = f"#{place+1}: {racer:<26}"
            if return_time:
                line = line + f"  {time:.3f} Seconds"
            report.append(line)

        if return_time:
            for racer, score in zip(status, [10, 9, 7, 2]):
                if racer[0] == self.racers[0].get_name():
                    report.append(f"\nMUSC TOTAL {score}")

        return "\n".join(report)

    def standings_diff(stand1, stand2):
        for line1, line2 in zip(stand1, stand2):
            if line1 != line2:
                return True
        return False

    def run_race(self):
        orig_standings = self.get_race_status(prog=0.0)
        print("Standings right off the line:")
        print(orig_standings+"\n")

        #SQRT makes stuff happen in the race sooner
        for time in np.linspace(0,0.999,250):
            standings = self.get_race_status(prog=time)

            if RaceTrack.standings_diff(standings, orig_standings):
                print(f"Standings at {time:.0%} point:")
                print(standings+"\n")
                orig_standings = standings


        print("FINAL RACE RESULTS:")
        print(self.get_race_status())


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

