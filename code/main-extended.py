import numpy as np
from gurobipy import GRB
import gurobipy as gp
from math import ceil
import pprint
import sys
from model.models import Article, Person, Track, Room
import os

if not os.path.exists('logs'):
    os.makedirs('logs')

cnT = {}
filename = "A50-P48-R5-B7-L2-T10-!1-!t3-C10.cs"

fp = open("instances/"+filename, "r")
lines = [line.strip() for line in fp.readlines() if line[0] != '#']
lines = iter(lines)
fp.close()


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
        waste[s][r] = abs(rooms[r].capacity-tracks[tt].attendance)

m = gp.Model("simple")
# x = m.addVars(nA, nS, vtype=GRB.BINARY, name='x')
x = m.addVars(nA, nS, nAS, vtype=GRB.BINARY, name='x')
y = m.addVars(nS, nR, nB, vtype=GRB.BINARY, name='y')
# w = m.addVars(nP, nS, vtype=GRB.BINARY, name='w')
w = m.addVars(nP, nS, nAS, vtype=GRB.BINARY, name='w')
bb = m.addVars(nS, vtype=GRB.BINARY, name='bb')
z = m.addVar(vtype=GRB.INTEGER, name='z')

c = m.addVars(nP, nS, vtype=GRB.BINARY, name='c')
o = m.addVars(nP, nS, vtype=GRB.BINARY, name='o')

nL = nAS

for a in range(nA):
    m.addConstr(sum(x[a, s, l] for s in range(nS) for l in range(nL)) ==
                1, name="Articulo-una-sola-vez")

for s in range(nS):
    m.addConstr(sum(x[a, s, l] for a in range(nA) for l in range(nL))
                <= nAS, name="Capacidad-Sesiones")

# RESTRICCION NUEVA
for s in range(nS):
    for l in range(nL):
        m.addConstr(sum(x[a, s, l] for a in range(nA))
                    <= 1, name="1-1-article-slot")


for s in range(nS):
    calc = sum(y[s, r, b] for r in range(nR) for b in range(nB))
    m.addConstr(calc == 1, name="Cada-sesion-una-vez")

for r in range(nR):
    for b in range(nB):
        calc = sum(y[s, r, b] for s in range(nS))
        m.addConstr(calc <= 1, name="celda-maximo-una-sesion")

for a in range(nA):
    for s in range(nS):
        if articles[a].track != sessions[s]:
            for l in range(nL):
                m.addConstr(x[a, s, l] == 0, name="Solo-en-sus-sesiones")

for a in range(nA):
    for s in range(nS):
        for l in range(nL):
            m.addConstr((x[a, s, l] == 1) >> (
                w[articles[a].author, s, l] == 1), name="author-asistance")

for a in range(nA):
    if articles[a].best:
        for s in range(nS):
            for l in range(nL):
                m.addConstr((x[a, s, l] == 1) >> (bb[s] == 1),
                            name="session-with-best")

for t in range(nT):
    for b in range(nB):
        calc = sum(y[s, r, b]*(1 if sessions[s] == t else 0)
                   for s in range(nS) for r in range(nR))
        m.addConstr(calc <= 1, name="avoid-parallel-tracks")

for p in range(nP):
    for s in range(nS):
        for l in range(nL):
            for r in range(nR):
                for b in people[p].conflicts:
                    m.addConstr(w[p, s, l]*y[s, r, b] == 0,
                                name="avoid-personal-conflicts")

# SKIP ROOM SIZE
# for s in range(nS):
#     for r in range(nR):
#         tt = sessions[s]
#         if tracks[tt].attendance > rooms[r].capacity:
#             for b in range(nB):
#                 m.addConstr(y[s, r, b] == 0, name="room-capacity")

m.addConstr(z == sum(y[s, r, b]*waste[s][r]
            for s in range(nS) for r in range(nR) for b in range(nB)), name="objective")

for p in range(nP):
    for b in range(nB):
        for l in range(nL):
            calc = sum(w[p, s, l]*y[s, r, b]
                       for s in range(nS) for r in range(nR))
            m.addConstr(calc <= 1, name="avoid-person-mitosis")

for b in range(nB):
    calc = sum(bb[s]*y[s, r, b] for s in range(nS) for r in range(nR))
    m.addConstr(calc <= 1, name="avoid-best-parallel")


for s in range(nS):
    for r in range(nR):
        for b in range(nB):
            t = sessions[s]
            pp = tracks[t].chairs
            m.addConstr((y[s, r, b] == 1) >> (sum(c[p, s]
                        for p in pp) >= 1), name="set-chair")

for p in range(nP):
    for s in range(nS):
        m.addConstr((c[p, s] == 1) >> (sum(w[p, s, l]
                    for l in range(nL)) == nL), name="if-chair-force-use-whole-session")

for s in range(nS):
    for r in range(nR):
        for b in range(nB):
            t = sessions[s]
            pp = tracks[t].organizers
            m.addConstr((y[s, r, b] == 1) >> (sum(o[p, s]
                        for p in pp) >= 1), name="set-organizers")

for p in range(nP):
    for s in range(nS):
        m.addConstr((o[p, s] == 1) >> (sum(w[p, s, l]
                    for l in range(nL)) == nL), name="if-organizers-force-use-whole-session")

m.setObjective(z, GRB.MINIMIZE)
m.write(f'logs/{filename}.lp')
m.optimize()
m.write(f'logs/{filename}.sol')


sessions = [{"people": [], "articles": [], "where":(
    0, 0), "chairs":[], "org":[]} for n in range(nS)]

for v in x.values():
    if v.X:
        art, ses, slot = eval(v.varName[1:])
        sessions[ses]["articles"].append((art, slot))

for v in y.values():
    if v.X:
        ses, room, block = eval(v.varName[1:])
        sessions[ses]["where"] = (room, block)

for v in w.values():
    if v.X:
        per, ses, slot = eval(v.varName[1:])
        sessions[ses]["people"].append((per, slot))

for v in c.values():
    if v.X:
        per, ses = eval(v.varName[1:])
        # print(art, ses)
        sessions[ses]["chairs"].append(per)

for v in o.values():
    if v.X:
        per, ses = eval(v.varName[1:])
        # print(art, ses)
        sessions[ses]["org"].append(per)

for ses in sessions:
    ses['people'].sort(key=lambda x: x[1])

for ses in sessions:
    block_all = [x[1] for x in ses['articles']]
    for nas in range(nAS):
        if nas not in block_all:
            ses['articles'].append((-1, nas))
    ses['articles'].sort(key=lambda x: x[1])
    # print(ses['articles'])
    # ses['people'] = [articles[e].author for e in ses['articles']]
    ses['articles'] = [(a[0], articles[a[0]].author if a[0]
                        != -1 else -1) for a in ses['articles']]

# print(sessions)

sessions.sort(key=lambda e: e["where"])

f_sessions = [[-1 for col in range(nB)] for row in range(nR)]
for ses in sessions:
    i, j = ses["where"]
    f_sessions[i][j] = ses

with open(f"logs/{filename}.sol", 'a') as f:
    for i in range(nR):
        for j in range(nB):
            ses = f_sessions[i][j]
            if ses != -1:
                print(*ses["articles"], end=";", sep=";", file=f)
                print(";", end="", file=f)
            else:
                print(*([-1]*nAS), end=";", sep=";", file=f)
                print(";", end="", file=f)
        print("\n", file=f)

    print("", file=f)

    for i in range(nR):
        for j in range(nB):
            ses = f_sessions[i][j]
            if ses != -1:
                print(*ses["chairs"], *ses["org"], end=";", sep="#", file=f)
                print(";", end=";", file=f)
            else:
                print(-1, end=";", sep=";", file=f)
                print(";", end=";", file=f)
        print("\n", file=f)
