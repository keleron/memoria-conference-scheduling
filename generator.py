from random import randint, choice
from random import random as u
from random import seed
from contextlib import redirect_stdout

seed(777)


def r(x, y): return randint(x, y-1)


def e_input(txt: str, default=0, type=int):
    res = input(txt+f" [{default}]:\n>>> ") or default
    return type(res)


nA = e_input("Cantidad de Articulos", 50)
nP = e_input("Cantidad de Personas", 48)
nR, nB, nAS = 0, 0, 0
while (nR*nR*nAS < nA):
    nR = e_input("Cantidad de Salones", 5)
    nB = e_input("Cantidad de Bloques/Horarios", 7)
    nAS = e_input("Cantidad de articulos por sesion", 2)
    if nR*nR*nAS < nA:
        print("\tNo hay espacio suficiente para planificar {nA} articulos!")

nT = e_input("Cantidad de Tracks", 10)
nSD = 4

nBest = e_input("Cantidad de Best Paper", 1)

tBest = float("inf")
while (tBest > nT):
    tBest = e_input(
        "Cuantos tracks distintos poseeran best papers (x<{nT})", 3)

nConf = e_input("Cantidad total de conflictos de persona", 10)

filename = f"A{nA}-P{nP}-R{nR}-B{nB}-L{nAS}-T{nT}-!{nBest}-!t{tBest}-C{nConf}.cs"
print(filename)

fp = open("instances/"+filename, "w")

with redirect_stdout(fp):
    print("# ARTICULOS	HUMANOS TOTAL	BLOQUES	SALONES	TRACKS	ARTICULOS POR SESION	SESIONES POR DIA")
    print(nA, nP, nB, nR, nT, nAS, nSD)
    print("#ARTICULO	TRACK	PRESENTADOR	BEST PAPER	")
    best_counter = 0
    for a in range(nA):
        tt = r(0, nT)
        best = 0
        if tt < tBest and best_counter < nBest:
            best_counter += 1
            best = 1
        print(a, tt, r(0, nP), best)

    people = []
    for p in range(nP):
        people.append([p, set()])

    for c in range(nConf):
        p = r(0, nP)
        bad = r(0, nB)
        people[p][1].add(bad)

    print("#PERSONA	CONFLICTO (CON TIEMPO)	")
    for p in people:
        print(p[0], ' '.join(map(str, list(p[1]))))

    print("#TRACK	ASISTENTES HISTORICOS	")
    for t in range(nT):
        print(t, randint(10, 30))

    print("#SALON	CAPACIDAD	")
    for r in range(nR):
        print(r, randint(15, 25))

    print("#TRACK	CHAIRS	")
    for t in range(nT):
        print(t, randint(0, nP-1), randint(0, nP-1))

    print("#TRACK	ORGANIZADORES	")
    for t in range(nT):
        print(t, randint(0, nP-1), randint(0, nP-1), randint(0, nP-1))

fp.close()
