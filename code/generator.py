from random import randint, choice
from random import random as u
from math import ceil, floor
from random import seed, sample, shuffle, choice
from contextlib import redirect_stdout
from model.models import Article, Person, Track
import os


def rr(x): return randint(0, x-1)


if not os.path.exists('instances'):
    os.makedirs('instances')


def jls_extract_def(nA, nP, nR, nB, nAS, nT, nConf):
    seed(777)
    filename = f"A{nA}-P{nP}-R{nR}-B{nB}-L{nAS}-T{nT}-C{nConf}.cs"
    nSD = 4
    nConf = int(floor(nP*nB*nConf))
    fp = open("instances/"+filename, "w")
    with redirect_stdout(fp):
        print("# ARTICULOS	HUMANOS TOTAL	BLOQUES	SALONES	TRACKS	ARTICULOS POR SESION	SESIONES POR DIA")
        print(nA, nP, nB, nR, nT, nAS, nSD)
        print("#ARTICULO	TRACK	PRESENTADOR	BEST PAPER	")

        tracks = [Track(t, 0) for t in range(nT)]
        articles = []
        for a in range(nA-4):
            tt = a % (nT-1)
            new_article = Article(a, tt, 0, 0)
            articles.append(new_article)
            tracks[tt].articles.append(new_article)

        for a in range(nA-4, nA):
            new_article = Article(a, nT-1, 0, 1)
            articles.append(new_article)
            tracks[tt].articles.append(new_article)

        for t in range(nT):
            tracks[t].sessions = ceil(len(tracks[t].articles)/nAS)

        nS = sum(tracks[t].sessions for t in range(nT))
        if (nS > nR*nB or (nR*nB-nS > 2)):
            fp.close()
            os.remove("instances/"+filename)
            return 0

        for track in tracks:
            if track.sessions > nB:
                fp.close()
                os.remove("instances/"+filename)
                return 0

        shuffle(articles)

        people = [Person(p, []) for p in range(nP)]
        shuffle(people)

        for a in range(nA):
            autor = a if a < nP else rr(nP-1)
            articles[a].author = people[autor]

        for track in tracks[:-4]:
            size = choice([3, 4])
            for a in sample(track.articles, size):
                a.best = 1

        articles.sort(key=lambda x: x.id)
        for a in articles:
            # ! PRIMER PRINT
            print(a.id, a.track, a.author.id, a.best)

        print("#PERSONA	CONFLICTO (CON TIEMPO)	")
        total_conf = 0

        people.sort(key=lambda x: x.id)
        while (total_conf < nConf):
            random_guy = choice(people)
            new_conflict = rr(nB)
            if new_conflict in random_guy.conflicts or len(random_guy.conflicts) > nB-1:
                continue
            random_guy.conflicts.append(new_conflict)
            total_conf += 1

        for p in people:
            print(str(p.id), ' '.join(str(c) for c in p.conflicts))

        print("#TRACK	ASISTENTES HISTORICOS	")
        for t in range(nT):
            print(t, randint(10, 30))

        print("#SALON	CAPACIDAD	")
        for r in range(nR):
            print(r, randint(15, 25))

        print("#TRACK	CHAIRS	")
        for t in range(nT):
            print(t, rr(nP), rr(nP))

        print("#TRACK	ORGANIZADORES	")
        for t in range(nT):
            print(t, rr(nP), rr(nP), rr(nP))
    print(filename)
    fp.close()
    return 1


# GECCO 8x7

articulos = [173]
tracks = [14]
salones = [5, 6, 7, 8, 9]
bloques = [6, 7, 8, 9]
por_session = [4, 5]
personas = [130, 150, 170]
conflictos = [0.10, 0.20, 0.30]

total = 0
for a in articulos:
    for t in tracks:
        for r in salones:
            for b in bloques:
                for l in por_session:
                    for p in personas:
                        for cc in conflictos:
                            total += jls_extract_def(a, p, r, b, l, t, cc)

print("instances generated", total)
