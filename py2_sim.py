import sys
import csv

class Racer:

    def _get_weight(params, S, P):
        w_battery = float(params['w_per_battery_cell']) * S * P
        return w_battery + float(params['w_dry'])

    def _get_speed(params, S, weight):
        return float(params['k_voltage']) * S - float(params['k_speed_weight']) * weight

    def _get_accel(params, P, weight):
        return float(params['k_current']) * P - float(params['k_torque_weight']) * weight

    def __init__(self, name, params=None, S=None, P=None, km, kp, cm, cp):
        self.name = name
        self.t_no_power = float(params['t_no_power'])
        self.k_speed = float(params['k_speed'])
        self.k_accel = float(params['k_accel'])

        if speed is None:
            weight = Racer._get_weight(params, S, P)
            self.speed=Racer._get_speed(params,S, weight)
        else:
            self.speed=speed
        if accel is None:
            weight = Racer._get_weight(params, S, P)
            self.accel=Racer._get_accel(params,P, weight)
        else:
            self.accel=accel

    def get_perf(self, prog):
        #prog = 1: (final) 50/50 torque and time
        #prog = 0: all torque
        return self.t_no_power - (self.accel * self.k_accel) + (prog * (self.speed * self.k_speed))

    def get_name(self):
        return self.name


def make_racers(params, S, P):
    racer_names = ["Tim Taylor", "Al Borland", "Mike Baxter", "Bob Vila"]

    tim = Racer(racer_names[0], params=params, S=S, P=P)

    racers = [tim]
    for i, name in enumerate(racer_names[1:]):
        comp_str = f"comp_{i}_"
        competitor = Racer(name, params=params,
                           speed=float(params[comp_str + "speed"]),
                           accel=float(params[comp_str + "accel"]))
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
        if student['username'].strip().lower() == username.strip().lower():
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

