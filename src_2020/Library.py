from operator import attrgetter
from collections import Counter

class Book:

    def __init__(self, ide, score):
        self.ide = ide
        self.score = score
        self.frq = 0

    @property
    def weighted_score(self):
        return self.score / self.frq

    @property
    def weighted_score2(self):
        return self.score * self.frq


    @property
    def get_score(self):
        return self.score

    @property
    def inv_frq(self):
        return 1 / self.frq


def mask_books(books, avoid):
    return [b for b in books if b not in avoid]
    # for book in books:
    #     if book not in avoid:
    #         yield book


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

    def worthy_books_first(self):
        return sorted(self.books, key=attrgetter("weighted_score"), reverse=True)

    def worthy_books_first2(self):
        return sorted(self.books, key=attrgetter("inv_frq"), reverse=True)
    
    def worthy_books_first3(self):
        return sorted(self.books, key=attrgetter("get_score"), reverse=True)
    
    def worthy_books_first4(self):
        return sorted(self.books, key=attrgetter("weighted_score2"), reverse=True)

    def nb_books_scannable(self, time_avail):
        time_bookflow = time_avail - self.signup
        return time_bookflow * self.ship

    def interest1(self, time_avail, avoid=set()):
        """A potential heuristic measure of library potential interest."""
        # time_bookflow = time_avail - self.signup
        # nb_books_scannable = time_bookflow // self.ship
        nb_books_scannable = self.nb_books_scannable(time_avail)
        return sum(b.weighted_score for b in mask_books(self.worthy_books_first(), avoid)[:nb_books_scannable])

    def interest2(self, time_avail, avoid=set()):
        """A potential heuristic measure of library potential interest."""
        # time_bookflow = time_avail - self.signup
        # nb_books_scannable = time_bookflow // self.ship
        nb_books_scannable = self.nb_books_scannable(time_avail)

        return sum(b.score for b in mask_books(self.worthy_books_first4(), avoid)[:nb_books_scannable])

    def interest3(self, time_avail, avoid=set()):
        """A potential heuristic measure of library potential interest."""
        # time_bookflow = time_avail - self.signup
        # nb_books_scannable = time_bookflow // self.ship
        nb_books_scannable = self.nb_books_scannable(time_avail)

        return sum(1/b.frq for b in mask_books(self.worthy_books_first2(), avoid)[:nb_books_scannable])

    def interest4(self, time_avail, avoid=set()):
        """A potential heuristic measure of library potential interest."""
        # time_bookflow = time_avail - self.signup
        # nb_books_scannable = time_bookflow // self.ship
        nb_books_scannable = self.nb_books_scannable(time_avail)

        return sum(b.score / b.frq for b in mask_books(self.worthy_books_first(), avoid)[:nb_books_scannable])

    def interest5(self, time_avail, avoid=set()):
        """A potential heuristic measure of library potential interest."""
        # time_bookflow = time_avail - self.signup
        # nb_books_scannable = time_bookflow // self.ship
        nb_books_scannable = self.nb_books_scannable(time_avail)

        return sum(b.frq for b in mask_books(self.worthy_books_first2(), avoid)[:nb_books_scannable])

    def interest6(self, time_avail, avoid=set()):
        """A potential heuristic measure of library potential interest."""
        # time_bookflow = time_avail - self.signup
        # nb_books_scannable = time_bookflow // self.ship
        nb_books_scannable = self.nb_books_scannable(time_avail)

        return sum(b.frq for b in mask_books(self.worthy_books_first2(), avoid)[:nb_books_scannable]) /(self.signup*self.ship)

    def interest7(self, time_avail, avoid=set()):
        """A potential heuristic measure of library potential interest."""
        # time_bookflow = time_avail - self.signup
        # nb_books_scannable = time_bookflow // self.ship
        nb_books_scannable = self.nb_books_scannable(time_avail)
        return sum(b.frq for b in mask_books(self.worthy_books_first2(), avoid)[:max(1,(nb_books_scannable*4)//5)]) /(self.signup*self.ship)
 
    def interest8(self, time_avail, avoid=set()):
        """A potential heuristic measure of library potential interest."""
        # time_bookflow = time_avail - self.signup
        # nb_books_scannable = time_bookflow // self.ship
        nb_books_scannable = self.nb_books_scannable(time_avail)
        return (1/nb_books_scannable*1/self.signup**2*self.ship)
 





