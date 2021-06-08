from random import randint, choice
from random import random as u
from random import seed


def r(x, y): return randint(x, y-1)


nA = 300
nP = 300
nB = 10
nR = 10
nT = 4
nAS = 4
nSD = 20

pp = {
    "best": 0.2,
    "conflicts": nA
}

if nT > nB:
    exit("more tracks than blocks")
if nA > nB*nR*nAS:
    exit("Not enough space")

print("# ARTICULOS	HUMANOS TOTAL	BLOQUES	SALONES	TRACKS	ARTICULOS POR SESION	SESIONES POR DIA")
print(nA, nP, nB, nR, nT, nAS, nSD)
print("#ARTICULO	TRACK	PRESENTADOR	BEST PAPER	")
for a in range(nA):
    best = 1 if u() < pp["best"] else 0
    print(a, r(0, nT), r(0, nP), best)

people = []
for p in range(nP):
    people.append([p, set()])

for c in range(pp["conflicts"]):
    p = r(0, nP)
    bad = r(0, nB)
    people[p][1].add(bad)

print("#PERSONA	CONFLICTO (CON TIEMPO)	")
for p in people:
    print(p[0], ' '.join(map(str, list(p[1]))))

print("#TRACK	ASISTENTES HISTORICOS	")
for t in range(nT):
    print(t, 10)

print("#SALON	CAPACIDAD	")
for r in range(nR):
    print(r, 10)

print("#TRACK	CHAIRS	")
for t in range(nT):
    print(t, randint(0, nP-1), randint(0, nP-1))

print("#TRACK	ORGANIZADORES	")
for t in range(nT):
    print(t, randint(0, nP-1), randint(0, nP-1), randint(0, nP-1))
