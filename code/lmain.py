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
filename = "A173-P160-R7-B8-L4-T13-C0.01.cs"
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
bb = m.addVars(nS, vtype=GRB.BINARY, name='bb')
z = m.addVar(vtype=GRB.INTEGER, name='z')

sigma1 = m.addVars(nP, nS, nR, nB, vtype=GRB.BINARY, name="sigma1")
# sigma2 = m.addVars(nS, nR, nB, vtype=GRB.BINARY, name="sigma2")


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
        p = articles[a].author
        m.addConstr(x[a, s] <= w[p, s], name="author-asistance")


for t in range(nT):
    with_best = [art for art in tracks[t].articles if art.best]
    for a in with_best:
        s = [i for i, s in enumerate(sessions) if s == t][0]
        m.addConstr(x[a.id, s] == 1, name="together-best-papers")


for t in range(nT):
    for b in range(nB):
        calc = sum(y[s, r, b]*(1 if sessions[s] == t else 0)
                   for s in range(nS) for r in range(nR))
        m.addConstr(calc <= 1, name="avoid-parallel-tracks")

for p in range(nP):
    for s in range(nS):
        for r in range(nR):
            for b in people[p].conflicts:
                m.addConstr(w[p, s]+y[s, r, b] <= 1,
                            name="avoid-personal-conflicts")


m.addConstr(z == sum(y[s, r, b]*waste[s][r]
            for s in range(nS) for r in range(nR) for b in range(nB)), name="objective")


# ? EVITAR PERSON MITOSIS
for p in range(nP):
    for b in range(nB):
        calc = sum(sigma1[p, s, r, b] for s in range(nS) for r in range(nR))
        m.addConstr(calc <= 1, name="avoid-person-mitosis")
for p in range(nP):
    for s in range(nS):
        for r in range(nR):
            for b in range(nB):
                m.addConstr(w[p, s]+y[s, r, b]-sigma1[p, s, r, b] <= 1)
                m.addConstr(sigma1[p, s, r, b] <= w[p, s])
                m.addConstr(sigma1[p, s, r, b] <= y[s, r, b])


for s in range(nS):
    for r in range(nR):
        for b in range(nB):
            t = sessions[s]
            cc, oo = tracks[t].chairs, tracks[t].organizers
            m.addConstr(y[s, r, b] <= sum(w[p, s]
                        for p in cc), name="set-chair-in-session")
            m.addConstr(y[s, r, b] <= sum(w[p, s]
                        for p in oo), name="set-org-in-session")


# ? ESTA DEL DESPERDICIO
m.setObjective(z, GRB.MINIMIZE)
# ? ESTA ES DE LOS BEST PAPER
# m.setObjectiveN(sum(sigma2[s, r, b] for s in range(nS)
#                 for r in range(nR) for b in range(nB)), 1, priority=1)

m.optimize()

if (m.Status == 3):
    exit("ERR: Model is infeasible -- ABORT")

m.write(f'logs/{filename}.lp')
m.write(f'logs/{filename}.simple.sol')


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
