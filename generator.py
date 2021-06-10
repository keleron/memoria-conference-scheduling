from random import randint, choice
from random import random as u
from random import seed

seed(777)


def r(x, y): return randint(x, y-1)


nA = 174
nP = 150
nR = 8
nB = 7
nT = 12
nAS = 4
nSD = 20

pp = {
    "best": 0.13,
    "conflicts": 200
}

filename = f"A{nA}-P{nP}-R{nR}-B{nB}-L{nAS}-T{nT}.cs"
print(filename)

fp = open("instances/"+filename, "w")


def print(*args):
    global fp
    line = ' '.join(map(str, args))+"\n"
    fp.write(line)


if nA > nB*nR*nAS:
    exit("Not enough space")

print("# ARTICULOS	HUMANOS TOTAL	BLOQUES	SALONES	TRACKS	ARTICULOS POR SESION	SESIONES POR DIA")
# fp.write("# ARTICULOS HUMANOS-TOTAL BLOQUES SALONES TRACKS ARTICULOS-POR-SESION SESIONES-POR-DIA")
print(nA, nP, nB, nR, nT, nAS, nSD)
print("#ARTICULO	TRACK	PRESENTADOR	BEST PAPER	")
for a in range(nA):
    tt = r(0, nT)
    best = 0
    if tt < 4:
        best = 1 if u() < pp["best"] else 0

    print(a, tt, r(0, nP), best)

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

fp.close()
