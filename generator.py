from random import randint, choice
from random import random as u
from random import seed

seed(777)


def r(x, y): return randint(x, y-1)


nA = 40
nP = 38
nR = 4
nB = 4
nAS = 3
nT = 5
nSD = 20

pp = {
    "best_track": 0,
    "best_amout": 0,
    "conflicts": 0,

}

nA = input(f"#ARTICULOS [ {nA} ] : ") or nA
nP = input(f"#PERSONAS  [ {nP} ] : ") or nP
nR = input(f"#SALONES   [ {nR} ] : ") or nR
nB = input(f"#BLOQUES   [ {nB} ] : ") or nB
nAS = input(f"#ARTICULOS POR SESION  [ {nAS} ] :") or nAS
nT = input(f"#TRACKS  [ {nT} ] : ") or nT

nA, nP, nR, nB, nAS, nT, nSD = map(int, [nA, nP, nR, nB, nAS, nT, nSD])


filename = f"A{nA}-P{nP}-R{nR}-B{nB}-L{nAS}-T{nT}.cs"
print(filename)

fp = open("instances/"+filename, "w")
best_counter = 0


def print(*args):
    global fp
    line = ' '.join(map(str, args))+"\n"
    fp.write(line)


if nA > nB*nR*nAS:
    exit("Not enough space")

print("# ARTICULOS	HUMANOS TOTAL	BLOQUES	SALONES	TRACKS	ARTICULOS POR SESION	SESIONES POR DIA")
print(nA, nP, nB, nR, nT, nAS, nSD)
print("#ARTICULO	TRACK	PRESENTADOR	BEST PAPER	")


for a in range(nA):
    tt = r(0, nT)
    best = 0
    if tt < pp['best_track'] and best_counter < pp['best_amout']:
        best = 1
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
