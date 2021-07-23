from math import ceil


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


def read_file(filename):
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

    for a in range(nA):
        aa, bb = articles[a].track, articles[a]
        tracks[articles[a].track].articles.append(articles[a])

    for t in range(nT):
        tracks[t].sessions = ceil(len(tracks[t].articles)/nAS)

    nS = sum(tracks[t].sessions for t in range(nT))
    sessions = []
    for t in range(nT):
        sessions += [tracks[t].id] * tracks[t].sessions

    return ((nA, nP, nB, nR, nT, nAS, nS), (articles, people, tracks, rooms, sessions))
