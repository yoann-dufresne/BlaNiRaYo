
class Book:

    def __init__(self, ide, score):
        self.ide = ide
        self.score = score
        self.frq = 0

    def __lt__(self, other):
        return self.score > other.score

    def __repr__(self):
        return f"{self.ide}({self.score})"

def mask_books(books, avoid):
    return [b for b in books if b not in avoid]


class Library:

    def __init__(self, ide, signup, ship, all_books):
        self.ide = ide
        # signup delay
        self.signup = signup
        # book "bandwidth"
        self.ship = ship
        # List of books
        self._books = all_books
        self.present_books = [False]* len(all_books)
        # List of books to scan /!\ ORDER IS IMPORTANT
        self.books_to_scan = []

    def __repr__(self):
        return str(self.ide)

    # def __lt__(self, other):
    #     return len(self.books) < len(other.books)

    def add_books(self, books):
        for b in books:
            self.present_books[b.ide] = True

    def books(self, avoid=set()):
        for idx, present in enumerate(self.present_books):
            if present and self._books[idx] not in avoid:
                yield self._books[idx]

    def sorted_books(self, avoid=set(), nb_days=-1):
        if nb_days < 0:
            return sorted(self.books(avoid))
        else:
            return sorted(self.books(avoid))[:nb_days*self.ship]

    def days_to_complete(self, avoid=set()):
        return self.signup + len(list(self.books(avoid))) / self.ship

    def queue_books_to_scan(self, books):
        self.books_to_scan.extend(books)

