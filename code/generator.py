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

        # for track in tracks[-4:]:
        #     sample(track.articles, 1)[0].best = 1

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
    return


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
people = [170, 150, 130]

jls_extract_def(55, 50, 4, 4, 4, 14, 0.12)
exit("done!")

for a, b, c in posibles:
    for p in people:
        for cc in conf:
            jls_extract_def(173, p, a, b, c, 14, cc)
