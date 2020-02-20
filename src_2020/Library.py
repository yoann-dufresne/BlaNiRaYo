from operator import attrgetter

class Book:

    def __init__(self, ide, score):
        self.ide = ide
        self.score = score
        self.frq = 0

    @property
    def weighted_score(self):
        return self.score / self.frq


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

    def __lt__(self, other):
        return len(self.books) < len(other.books)

    def add_books(self, books):
        self.books.extend(books)

    def add_books_to_scan(self, books):
        self.books_to_scan.extend(books)

    def worthy_books_first(self, time_available):
        return sorted(self.books, key=attrgetter("weighted_score"), reverse=True)[:time_available*self.ship]

    def nb_books_scannable(self, time_avail):
        time_bookflow = time_avail - self.signup
        return time_bookflow // self.ship

    def interest1(self, time_avail, avoid=set()):
        """A potential heuristic measure of library potential interest."""
        # time_bookflow = time_avail - self.signup
        # nb_books_scannable = time_bookflow // self.ship
        nb_books_scannable = self.nb_books_scannable(time_avail-self.signup)

        return sum(b.score for b in mask_books(self.worthy_books_first(time_avail-self.signup)[:nb_books_scannable], avoid))

    def interest2(self, time_avail, avoid=set()):
        """A potential heuristic measure of library potential interest. using frequencies"""
        # time_bookflow = time_avail - self.signup
        # nb_books_scannable = time_bookflow // self.ship
        nb_books_scannable = self.nb_books_scannable(time_avail-self.signup)

        return sum(b.score for b in mask_books(self.worthy_books_first(time_avail-self.signup)[:nb_books_scannable], avoid))


