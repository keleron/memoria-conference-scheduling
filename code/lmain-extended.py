import os
import pprint
import sys
from math import ceil

import gurobipy as gp
import numpy as np
from gurobipy import GRB

from model.models import Article, Person, Room, Track

if not os.path.exists('solutions'):
    os.makedirs('solutions')
if not os.path.exists('lp-files'):
    os.makedirs('lp-files')


def solve_all(filename):
    # filename = "A173-P130-R5-B8-L5-T14-C0.2.cs"
    print(f"-----------------------STARTING {filename}")

    fp = open("instances/"+filename, "r")
    lines = [line.strip() for line in fp.readlines() if line[0] != '#']
    lines = iter(lines)
    fp.close()

    def _next():

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

    x = m.addVars(nA, nS, nAS, vtype=GRB.BINARY, name='x')
    y = m.addVars(nS, nR, nB, vtype=GRB.BINARY, name='y')

    w = m.addVars(nP, nS, nAS, vtype=GRB.BINARY, name='w')
    # bb = m.addVars(nS, vtype=GRB.BINARY, name='bb')
    z = m.addVar(vtype=GRB.INTEGER, name='z')

    c = m.addVars(nP, nS, vtype=GRB.BINARY, name='c')
    o = m.addVars(nP, nS, vtype=GRB.BINARY, name='o')

    nL = nAS
    sigma1 = m.addVars(nP, nS, nL, nR, nB, vtype=GRB.BINARY, name="sigma1")
    # sigma2 = m.addVars(nS, nR, nB, vtype=GRB.BINARY, name="sigma2")

    qsum = gp.quicksum
    for a in range(nA):
        m.addConstr(qsum(x[a, s, l] for s in range(nS) for l in range(nL)) ==
                    1, name="Articulo-una-sola-vez")

    for s in range(nS):
        m.addConstr(qsum(x[a, s, l] for a in range(nA) for l in range(nL))
                    <= nAS, name="Capacidad-Sesiones")

    for s in range(nS):
        for l in range(nL):
            m.addConstr(qsum(x[a, s, l] for a in range(nA))
                        <= 1, name="1-1-article-slot")

    for s in range(nS):
        calc = qsum(y[s, r, b] for r in range(nR) for b in range(nB))
        m.addConstr(calc == 1, name="Cada-sesion-una-vez")

    for r in range(nR):
        for b in range(nB):
            calc = qsum(y[s, r, b] for s in range(nS))
            m.addConstr(calc <= 1, name="celda-maximo-una-sesion")

    for a in range(nA):
        for s in range(nS):
            if articles[a].track != sessions[s]:
                # for l in range(nL):
                m.addConstr(qsum(x[a, s, l] for l in range(nL))
                            == 0, name="Solo-en-sus-sesiones")

    for a in range(nA):
        for s in range(nS):
            for l in range(nL):
                p = articles[a].author
                m.addConstr(x[a, s, l] <= w[p, s, l],
                            name="author-asistance")

    for t in range(nT):
        with_best = [art for art in tracks[t].articles if art.best]
        for a in with_best:
            ses_id = [i for i, s in enumerate(sessions) if s == t][0]
            m.addConstr(qsum(x[a.id, ses_id, l]
                        for l in range(nL)) == 1, name="together-best-papers")
            # for ii, sis in enumerate(sessions):
            #     if ii == ses_id:
            #         continue
            #     # for l in range(nL):
            #     m.addConstr(qsum(x[a.id, ii, l] for l in range(nL)) == 0,
            #               name = "together-best-papers")

    for t in range(nT):
        for b in range(nB):
            calc = qsum(y[s, r, b] for s in range(nS)
                        for r in range(nR) if sessions[s] == t)
            m.addConstr(calc <= 1, name="avoid-parallel-tracks")

    for p in range(nP):
        for s in range(nS):
            for l in range(nL):
                for r in range(nR):
                    for b in people[p].conflicts:
                        m.addConstr(w[p, s, l]+y[s, r, b] <= 1,
                                    name="avoid-personal-conflicts")

    print("CONSTRUYENDO LA PARTE MAS GRANDE DEL MODELO...")
    # ! ESTO ES PARTE DE LA MITOSIS
    for p in range(nP):
        for b in range(nB):
            for l in range(nL):
                m.addConstr(qsum(sigma1[p, s, l, r, b]
                            for s in range(nS) for r in range(nR)) <= 1)

    for p in range(nP):
        for s in range(nS):
            for l in range(nL):
                for r in range(nR):
                    for b in range(nB):
                        m.addConstr(w[p, s, l]+y[s, r, b] -
                                    sigma1[p, s, l, r, b] <= 1)
    for p in range(nP):
        for s in range(nS):
            for l in range(nL):
                m.addConstr(qsum(sigma1[p, s, l, r, b] for r in range(nR)
                            for b in range(nB)) <= nR * nB * w[p, s, l])
    for s in range(nS):
        for r in range(nR):
            for b in range(nB):
                m.addConstr(qsum(sigma1[p, s, l, r, b] for p in range(nP)
                            for l in range(nL)) <= nP * nL * y[s, r, b])

    print("DONE WITH IT!")

    for s in range(nS):
        for r in range(nR):
            for b in range(nB):
                t = sessions[s]
                cc = tracks[t].chairs
                oo = tracks[t].organizers
                m.addConstr(y[s, r, b] <= qsum(c[p, s]
                            for p in cc), name="set-chair")
                m.addConstr(y[s, r, b] <= qsum(o[p, s]
                            for p in oo), name="set-organizers")

    for t in tracks:
        for s in range(nS):
            for p in t.chairs:
                sum_w_psl = qsum(w[p, s, l] for l in range(nL))
                m.addConstr(nL*c[p, s] <= sum_w_psl,
                            name="if-chair-force-use-whole-session")
            for p in t.organizers:
                sum_w_psl = qsum(w[p, s, l] for l in range(nL))
                m.addConstr(nL*o[p, s] <= sum_w_psl,
                            name="if-organizers-force-use-whole-session")

    m.setObjective(qsum(y[s, r, b]*waste[s][r]
                        for s in range(nS) for r in range(nR) for b in range(nB) if waste[s][r] != 0), GRB.MINIMIZE)

    m.write(f"lp-files/{filename}.lp")
    m.optimize()

    with open("gurobi.log", "a") as fp:
        fp.write("DEBUG: "+filename+"\n")

    if (m.status == 3 or (m.status == 9 and m.SolCount == 0)):  # 9
        message = "INFEASIBLE" if m.Status == 3 else "TIME LIMIT INFEASIBLE"
        with open(f"solutions/{filename}.sol", "a+") as fp:
            fp.write("INFEASIBLE")
        with open("short.log", "a+") as fp:
            fp.write(
                f"{filename}; ---; ---; ---; {round(m.Runtime, 2)}; {message}\n")
        return

    obj = m.getObjective()
    message = "TIMELIMIT" if m.status == 9 else "FEASIBLE"
    with open("short.log", "a+") as fp:
        line = ';'.join(map(str, [filename, obj.getValue(), m.ObjBound, m.MIPGap,
                                  round(m.Runtime, 2), message, "\n"]))
        fp.write(line)

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
            sessions[ses]["chairs"].append(per)

    for v in o.values():
        if v.X:
            per, ses = eval(v.varName[1:])
            sessions[ses]["org"].append(per)

    for ses in sessions:
        ses['people'].sort(key=lambda x: x[1])

    for ses in sessions:
        block_all = [x[1] for x in ses['articles']]
        for nas in range(nAS):
            if nas not in block_all:
                ses['articles'].append((-1, nas))
        ses['articles'].sort(key=lambda x: x[1])
        ses['articles'] = [(a[0], articles[a[0]].author if a[0]
                            != -1 else -1) for a in ses['articles']]

    sessions.sort(key=lambda e: e["where"])

    f_sessions = [[-1 for col in range(nB)] for row in range(nR)]
    for ses in sessions:
        i, j = ses["where"]
        f_sessions[i][j] = ses

    with open(f"solutions/{filename}.sol", 'w') as f:
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
                    print(*ses["chairs"], *ses["org"],
                          end=";", sep="#", file=f)
                    print(";", end=";", file=f)
                else:
                    print(-1, end=";", sep=";", file=f)
                    print(";", end=";", file=f)
            print("\n", file=f)


posibles = [
    [5, 8, 5],
    [5, 9, 5],
    [6, 7, 5],
    [6, 8, 4],
    [6, 9, 4],
    [7, 6, 5],
    [7, 7, 4],
    [7, 8, 4],
    [8, 6, 4],
    [8, 7, 4],
]

conf = [0.10, 0.20, 0.30]
people = [130, 150, 170]


solve_all("A55-P50-R4-B4-L4-T14-C0.12.cs")


# for r, b, l in posibles:
#     for p in people:
#         for c in conf:
#             name = f"A173-P{p}-R{r}-B{b}-L{l}-T14-C{c}.cs"
#             # print(name)
#             if os.path.exists(f'solutions/{name}.sol'):
#                 print("SKIP", name)
#             else:
#                 solve_all(name)

timed = ["A173-P130-R5-B8-L5-T14-C0.3.cs",
         "A173-P170-R5-B8-L5-T14-C0.2.cs",
         "A173-P130-R5-B9-L5-T14-C0.3.cs",
         "A173-P170-R5-B9-L5-T14-C0.3.cs",
         "A173-P150-R6-B7-L5-T14-C0.2.cs",
         "A173-P170-R6-B7-L5-T14-C0.2.cs",
         "A173-P130-R6-B9-L4-T14-C0.3.cs",
         "A173-P150-R6-B9-L4-T14-C0.2.cs",
         "A173-P170-R6-B9-L4-T14-C0.3.cs",
         "A173-P130-R7-B6-L5-T14-C0.2.cs",
         "A173-P150-R7-B6-L5-T14-C0.2.cs",
         "A173-P170-R7-B6-L5-T14-C0.2.cs",
         "A173-P130-R7-B8-L4-T14-C0.1.cs",
         "A173-P130-R7-B8-L4-T14-C0.2.cs",
         "A173-P130-R7-B8-L4-T14-C0.3.cs",
         "A173-P150-R7-B8-L4-T14-C0.2.cs",
         "A173-P170-R7-B8-L4-T14-C0.2.cs"]

for name in timed:
    solve_all(name)
