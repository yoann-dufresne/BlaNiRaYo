
class Solution:

    def __init__(self, libs=[]):
        self.libs = [lib for lib in libs]

    def set_all_books(self, nb_days):
        for lib in self.libs:
            lib.books_to_scan = []
        forbiden = set()

        for lib in self.libs:
            nb_days -= lib.signup
            for book in lib.sorted_books(forbiden, nb_days):
                forbiden.add(book)
                lib.books_to_scan.append(book)

    def get_score(self):
        books = set()
        for lib in self.libs:
            books = books.union(set(lib.books_to_scan))

        return sum(book.score for book in books)
