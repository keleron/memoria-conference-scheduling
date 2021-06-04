import numpy as np
from gurobipy import GRB
import gurobipy as gp
from math import ceil
import pprint
pp = pprint.PrettyPrinter(indent=4).pprint


class Article:
    def __init__(self, id, track, author, best):
        self.id = id
        self.track = track
        self.author = author
        self.best = best


class Person:
    def __init__(self, id, conflicts):
        self.id = id
        self.conflicts = conflicts


class Track:
    def __init__(self, id, attendance):
        self.id = id
        self.attendance = attendance
        self.articles = []
        self.chairs = []
        self.organizers = []
        self.sessions = 0


class Room:
    def __init__(self, id, capacity):
        self.id = id
        self.capacity = capacity


cnT = {}
fp = open("MAGNIFIC.csv", "r")
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


m = gp.Model("simple")
x = m.addVars(nA, nS, vtype=GRB.BINARY, name='x')
y = m.addVars(nS, nR, nB, vtype=GRB.BINARY, name='y')
w = m.addVars(nP, nS, vtype=GRB.BINARY, name='w')
bb = m.addVars(nS, vtype=GRB.BINARY, name='bb')
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

for a in range(nA):
    if articles[a].best:
        for s in range(nS):
            m.addConstr((x[a, s] == 1) >> (bb[s] == 1),
                        name="session-with-best")

for t in range(nT):
    for b in range(nB):
        calc = sum(y[s, r, b]*(1 if sessions[s] == t else 0)
                   for s in range(nS) for r in range(nR))
        m.addConstr(calc <= 1, name="avoid-parallel-tracks")

for p in range(nP):
    for s in range(nS):
        for r in range(nR):
            for b in people[p].conflicts:
                m.addConstr(w[p, s]*y[s, r, b] == 0,
                            name="avoid-personal-conflicts")

# SKIP ROOM SIZE

for p in range(nP):
    for b in range(nB):
        calc = sum(w[p, s]*y[s, r, b] for s in range(nS) for r in range(nR))
        m.addConstr(calc <= 1, name="avoid-person-mitosis")

for b in range(nB):
    calc = sum(bb[s]*y[s, r, b] for s in range(nS) for r in range(nR))
    m.addConstr(calc <= 1, name="avoid-best-parallel")

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
m.optimize()
m.write('csTrackSolver.lp')
m.write('csTrackSolver.sol')
