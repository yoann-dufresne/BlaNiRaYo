
class Library:

    def __init__(self, signup, ship):
        self.signup = signup
        self.ship = ship
        self.books = []

    def add_books(self, books):
        self.books = books

class Book:

    def __init__(self, ide, score):
        self.ide = ide
        self.score = score
