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
filename = "A174-P150-R8-B7-L4-T12.cs"
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
            pp = tracks[t].chairs
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
