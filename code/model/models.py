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
