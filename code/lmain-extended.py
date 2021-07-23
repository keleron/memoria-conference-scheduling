import os
import pprint
import sys
from math import ceil

import gurobipy as gp
import numpy as np
from gurobipy import GRB
from contextlib import redirect_stdout
from model.models import Article, Person, Room, Track, read_file
from os import listdir
from os.path import isfile, join

if not os.path.exists('solutions'):
    os.makedirs('solutions')


def solve_all(filename):
    print("="*60 + "\n[INFO]: STARTING " + filename)
    if os.path.exists(f"solutions/{filename}.sol") or os.path.exists(f"solutions/{filename}.sol.plain"):
        print(f"[WARN] INSTANCE ALREADY SOLVED, SKIPPING")
        return 0

    with open("gurobi.log", "a+") as fp:
        fp.write("="*60 + "\n[INFO]: STARTING " + filename+"\n")
        # return 1

    linear = True
    cte, objs = read_file(filename)
    nA, nP, nB, nR, nT, nAS, nS = cte
    articles, people, tracks, rooms, sessions = objs

    waste = [[0 for r in range(nR)]for s in range(nS)]
    for s in range(nS):
        for r in range(nR):
            tt = sessions[s]
            waste[s][r] = rooms[r].capacity-tracks[tt].attendance
            waste[s][r] = abs(waste[s][r]) if waste[s][r] < 0 else 0
    print("[INFO] SUCCESS READ")

    m = gp.Model("simple")
    x = m.addVars(nA, nS, nAS, vtype=GRB.BINARY, name='x')
    y = m.addVars(nS, nR, nB, vtype=GRB.BINARY, name='y')
    w = m.addVars(nP, nS, nAS, vtype=GRB.BINARY, name='w')
    z = m.addVar(vtype=GRB.INTEGER, name='z')
    c = m.addVars(nP, nS, vtype=GRB.BINARY, name='c')
    o = m.addVars(nP, nS, vtype=GRB.BINARY, name='o')
    nL = nAS
    sigma1 = m.addVars(nP, nS, nL, nR, nB, vtype=GRB.BINARY, name="sigma1")

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
                m.addConstr(qsum(x[a, s, l] for l in range(nL))
                            == 0, name="Solo-en-sus-sesiones")

    for a in range(nA):
        for s in range(nS):
            for l in range(nL):
                p = articles[a].author
                if (linear):
                    m.addConstr(x[a, s, l] <= w[p, s, l],
                                name="author-asistance")
                else:
                    m.addConstr((x[a, s, l] == 1) >> (
                        w[articles[a].author, s, l] == 1), name="author-asistance")

    for t in range(nT):
        with_best = [art for art in tracks[t].articles if art.best]
        for a in with_best:
            ses_id = [i for i, s in enumerate(sessions) if s == t][0]
            m.addConstr(qsum(x[a.id, ses_id, l]
                        for l in range(nL)) == 1, name="together-best-papers")

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
                        if (linear):
                            m.addConstr(w[p, s, l]+y[s, r, b] <=
                                        1, name="avoid-personal-conflicts")
                        else:
                            m.addConstr(w[p, s, l]*y[s, r, b] == 0,
                                        name="avoid-personal-conflicts")
    if linear:
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

    print("[INFO] MODEL CREATED, STARTING SOLVER")
    m.optimize()
    print("[INFO] SOLVER HAS STOPPED")

    if (m.Status == 2):
        with open("short.log", "a+") as fp:
            to_write = [filename, m.objVal, m.ObjBound, m.MIPGap,
                        round(m.Runtime), "OPTIMAL\n"]
            fp.write(';'.join(map(str, to_write)))

    if (m.Status == 3):
        with open("short.log", "a+") as fp:
            fp.write(f"{filename};;;;{round(m.Runtime, 2)}; INFEASIBLE\n")

    if (m.Status == 9):
        with open("short.log", "a+") as fp:
            if (m.SolCount == 0):
                fp.write(f"{filename};;;;{round(m.Runtime, 2)}; TIME\n")
            if (m.SolCount > 0):
                to_write = [filename, m.objVal, m.ObjBound, m.MIPGap,
                            round(m.Runtime), "TIME\n"]
                fp.write(';'.join(map(str, to_write)))

    fp = open(f"solutions/{filename}.sol.plain", "w")
    with redirect_stdout(fp):
        if (m.SolCount > 0):
            print(m.objVal, m.ObjBound, m.MIPGap, m.Runtime)
            for v in m.getVars():
                if v.X:
                    print('%s %g' % (v.varName, v.x))
        else:
            print("INF", "-", "-", m.Runtime)
    return 0


onlyfiles = [f for f in listdir("./instances/")
             if isfile(join("./instances/", f))]
onlyfiles = [f for f in onlyfiles if f[-3:] == ".cs"]

total = 0
for file in onlyfiles:
    solve_all(file)
print("unsolved", total, "from", len(onlyfiles))
