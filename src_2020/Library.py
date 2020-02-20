from operator import attrgetter

class Book:

    def __init__(self, ide, score):
        self.ide = ide
        self.score = score


def mask_books(books, avoid):
    for book in books:
        if book not in avoid:
            yield book


class Library:

    def __init__(self, ide, signup, ship):
        self.ide = ide
        # signup delay
        self.signup = signup
        # book "bandwidth"
        self.ship = ship
        # List of books
        self.books = []
        # List of books to scan /!\ ORDER IS IMPORTANT
        self.books_to_scan = []

    def add_books(self, books):
        self.books.extend(books)

    def add_books_to_scan(self, books):
        self.books_to_scan.append(books)

    def sort_books(self):
        pass


    @property
    def worthy_books_first(self):
        return sorted(self.books, key=attrgetter("score"), reverse=True)

    def interest1(self, time_avail, avoid=set()):
        """A potential heuristic measure of library potential interest."""
        time_bookflow = time_avail - self.signup
        nb_books_scannable = time_bookflow // self.ship

        return sum(b.score for b in mask_books(self.worthy_books_first[:nb_books_scannable], avoid))


