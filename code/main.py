import numpy as np
from gurobipy import GRB
import gurobipy as gp
from math import ceil
import pprint
from contextlib import redirect_stdout
from model.models import Article, Person, Track, Room
import os

if not os.path.exists('logs'):
    os.makedirs('logs')

cnT = {}
filename = "A173-P170-R6-B9-L4-T14-C0.3.cs"
fp = open("instances/"+filename, "r")

lines = [line.strip() for line in fp.readlines() if line[0] != '#']
lines = iter(lines)


def _next():
    global lines
    return map(int, next(lines).split())


nA, nP, nB, nR, nT, nAS, _ = map(int, next(lines).split())
articles = []
people = []
tracks = []
rooms = []

for a in range(nA):
    articles.append(Article(*_next()))

for p in range(nP):
    id, *conf = _next()
    people.append(Person(id, conf))

for t in range(nT):
    tracks.append(Track(*_next()))

for r in range(nR):
    rooms.append(Room(*_next()))

for t in range(nT):
    _, *somes = _next()
    tracks[t].chairs += somes

for t in range(nT):
    _, *somes = _next()
    tracks[t].organizers += somes


print("READING DONE")
for a in range(nA):
    aa, bb = articles[a].track, articles[a]
    tracks[articles[a].track].articles.append(articles[a])

for t in range(nT):
    tracks[t].sessions = ceil(len(tracks[t].articles)/nAS)

nS = sum(tracks[t].sessions for t in range(nT))
sessions = []
for t in range(nT):
    sessions += [tracks[t].id] * tracks[t].sessions


waste = [[0 for r in range(nR)]for s in range(nS)]
for s in range(nS):
    for r in range(nR):
        tt = sessions[s]
        waste[s][r] = rooms[r].capacity-tracks[tt].attendance
        waste[s][r] = abs(waste[s][r]) if waste[s][r] < 0 else 0

m = gp.Model("simple")
x = m.addVars(nA, nS, vtype=GRB.BINARY, name='x')
y = m.addVars(nS, nR, nB, vtype=GRB.BINARY, name='y')
w = m.addVars(nP, nS, vtype=GRB.BINARY, name='w')
z = m.addVar(vtype=GRB.INTEGER, name='z')


for a in range(nA):
    m.addConstr(sum(x[a, s] for s in range(nS)) ==
                1, name="Articulo-una-sola-vez")

for s in range(nS):
    m.addConstr(sum(x[a, s] for a in range(nA))
                <= nAS, name="Capacidad-Sesiones")

for s in range(nS):
    calc = sum(y[s, r, b] for r in range(nR) for b in range(nB))
    m.addConstr(calc == 1, name="Cada-sesion-una-vez")

for r in range(nR):
    for b in range(nB):
        calc = sum(y[s, r, b] for s in range(nS))
        m.addConstr(calc <= 1, name="Bloques-maximo-una-sesion")

for a in range(nA):
    for s in range(nS):
        if articles[a].track != sessions[s]:
            m.addConstr(x[a, s] == 0, name="Solo-en-sus-sesiones")

for a in range(nA):
    for s in range(nS):
        m.addConstr((x[a, s] == 1) >> (w[articles[a].author, s]
                    == 1), name="author-asistance")

for t in range(nT):
    with_best = [art for art in tracks[t].articles if art.best]
    for a in with_best:
        ses_id = [i for i, s in enumerate(sessions) if s == t][0]
        m.addConstr(x[a.id, ses_id] == 1, name="together-best-papers")

for t in range(nT):
    for b in range(nB):
        calc = sum(y[s, r, b] for s in range(nS)
                   for r in range(nR) if sessions[s] == t)
        m.addConstr(calc <= 1, name="avoid-parallel-tracks")

for p in range(nP):
    for s in range(nS):
        for r in range(nR):
            for b in people[p].conflicts:
                m.addConstr(w[p, s]*y[s, r, b] == 0,
                            name="avoid-personal-conflicts")

m.addConstr(z == sum(y[s, r, b]*waste[s][r] for s in range(nS)
            for r in range(nR) for b in range(nB) if waste[s][r] != 0), name="objective")

for p in range(nP):
    for b in range(nB):
        calc = sum(w[p, s]*y[s, r, b] for s in range(nS) for r in range(nR))
        m.addConstr(calc <= 1, name="avoid-person-mitosis")

for s in range(nS):
    for r in range(nR):
        for b in range(nB):
            t = sessions[s]
            pp = tracks[t].chairs
            m.addConstr((y[s, r, b] == 1) >> (sum(w[p, s]
                        for p in pp) >= 1), name="set-chair-in-session")


for s in range(nS):
    for r in range(nR):
        for b in range(nB):
            t = sessions[s]
            pp = tracks[t].organizers
            m.addConstr((y[s, r, b] == 1) >> (sum(w[p, s]
                        for p in pp) >= 1), name="set-org-in-session")

m.setObjective(z, GRB.MINIMIZE)
# if os.path.exists(f"logs/{filename}.simple.sol"):
#     print("\tREADING HINT")
#     m.read(f"logs/{filename}.simple.sol")

m.optimize()
if not m.Status == 2:
    exit("something not feasible")

m.write(f'logs/{filename}.simple.lp')
m.write(f'logs/{filename}.simple.sol')


# for v in m.getVars():
#     print(v.x)

sessions = [{"people": [], "articles": [], "where":(0, 0)} for n in range(nS)]

for v in x.values():
    if v.X:
        art, ses = eval(v.varName[1:])
        # print(art, ses)
        sessions[ses]["articles"].append(art)

for v in y.values():
    if v.X:
        ses, room, block = eval(v.varName[1:])
        sessions[ses]["where"] = (room, block)

for v in w.values():
    if v.X:
        per, ses = eval(v.varName[1:])
        # print(art, ses)
        sessions[ses]["people"].append(per)


def superSort(e):
    return e["where"]


fp = open(f"logs/{filename}.simple.sol", 'a')

with redirect_stdout(fp):
    sessions.sort(key=superSort)
    # print(sessions)
    f_sessions = [[0 for col in range(nB)] for row in range(nR)]
    for ses in sessions:
        i, j = ses["where"]
        f_sessions[i][j] = ses

    for row in f_sessions:
        for col in row:
            if col != 0:
                print(str(col["articles"])+"#"+str(col["people"]), end=";")
            else:
                print("-1", end=";")
        print("\n")

fp.close()
