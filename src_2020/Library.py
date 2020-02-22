from operator import attrgetter
from collections import Counter


get_score = attrgetter("score")


class Book:
    __slots__ = ("ide", "score", "frq")

    def __init__(self, ide, score):
        self.ide = ide
        self.score = score
        self.frq = 0

    @property
    def weighted_score(self):
        return self.score / self.frq

    @property
    def inv_frq(self):
        return 1 / self.frq


def mask_books(books, avoid):
    return [b for b in books if b not in avoid]


class Library:
    __slots__ = ("ide", "signup", "ship", "books", "books_to_scan", "signed", "urgency", "invship")

    def __init__(self, ide, signup, ship):
        self.ide = ide
        # signup delay
        self.signup = signup
        # book "bandwidth"
        self.ship = ship
        self.invship = 1.0 / ship
        # A library should be queried early if it has
        # - a long signup time
        # - low shipping capacity
        # - lots of (valuable) books
        self.urgency = self.signup / self.ship
        # List of books
        self.books = []
        # List of books to scan /!\ ORDER IS IMPORTANT
        self.books_to_scan = []
        # has the library been signed into?
        self.signed = False

    def __lt__(self, other):
        return len(self.books) < len(other.books)

    @property
    def libsize(self):
        return len(self.books)

    @property
    def daysneed(self):
        """
        Number of days necessary to signup and send all books
        """
        return (len(self.books) / self.ship) + self.signup

    @property
    def invdaysneed(self):
        return 1 / self.daysneed

    @property
    def libworth(self):
        return sum(map(get_score, self.books))

    def add_books(self, books):
        self.books.extend(books)
        # Might speed up removal if high scores tend to be removed first
        self.books.sort(key=get_score)

    def add_books_to_scan(self, books):
        self.books_to_scan.extend(books)

    def books_by_worth(self, book_quality_fun=get_score, time_available=None, avoid=set()):
        if time_available is None:
            return sorted(
                mask_books(self.books, avoid),
                key=book_quality_fun, reverse=True)
        elif self.signed:
            return sorted(
                mask_books(self.books, avoid),
                key=book_quality_fun, reverse=True)[:time_available * self.ship]
        else:
            return sorted(
                mask_books(self.books, avoid),
                key=book_quality_fun, reverse=True)[:max(0, time_available - self.signup) * self.ship]

    def worthy_books_first(self, time_available):
        return sorted(self.books, key=attrgetter("weighted_score"), reverse=True)[:time_available*self.ship]

    def worthy_books_first2(self, time_available):
        return sorted(self.books, key=attrgetter("inv_frq"), reverse=True)[:time_available*self.ship]

    def nb_books_scannable(self, time_avail):
        time_bookflow = time_avail - self.signup
        return time_bookflow // self.ship

    def interest1(self, time_avail, avoid=set()):
        """A potential heuristic measure of library potential interest."""
        # time_bookflow = time_avail - self.signup
        # nb_books_scannable = time_bookflow // self.ship
        nb_books_scannable = self.nb_books_scannable(time_avail-self.signup)

        return sum(b.weighted_score for b in mask_books(self.worthy_books_first(time_avail-self.signup)[:nb_books_scannable], avoid))

    def interest2(self, time_avail, avoid=set()):
        """A potential heuristic measure of library potential interest."""
        # time_bookflow = time_avail - self.signup
        # nb_books_scannable = time_bookflow // self.ship
        nb_books_scannable = self.nb_books_scannable(time_avail-self.signup)

        return sum(b.score for b in mask_books(self.worthy_books_first(time_avail-self.signup)[:nb_books_scannable], avoid))

    def interest3(self, time_avail, avoid=set()):
        """A potential heuristic measure of library potential interest."""
        # time_bookflow = time_avail - self.signup
        # nb_books_scannable = time_bookflow // self.ship
        nb_books_scannable = self.nb_books_scannable(time_avail-self.signup)

        return sum(1/b.frq for b in mask_books(self.worthy_books_first2(time_avail-self.signup)[:nb_books_scannable], avoid))

    def interest4(self, time_avail, avoid=set()):
        """A potential heuristic measure of library potential interest."""
        # time_bookflow = time_avail - self.signup
        # nb_books_scannable = time_bookflow // self.ship
        nb_books_scannable = self.nb_books_scannable(time_avail-self.signup)

        return sum(b.score / b.frq for b in mask_books(self.worthy_books_first(time_avail-self.signup)[:nb_books_scannable], avoid))

    def interest5(self, time_avail, avoid=set()):
        """A potential heuristic measure of library potential interest."""
        # time_bookflow = time_avail - self.signup
        # nb_books_scannable = time_bookflow // self.ship
        nb_books_scannable = self.nb_books_scannable(time_avail-self.signup)

        return sum(b.frq for b in mask_books(self.worthy_books_first2(time_avail-self.signup)[:nb_books_scannable], avoid))
