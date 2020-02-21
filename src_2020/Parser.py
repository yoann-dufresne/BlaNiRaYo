import sys
from collections import Counter
from src_2020.Library import Library, Book

def parse(source=None):
    if source is None:
        source = sys.stdin
    else:
        source = open(source)
    [nb_books, nb_libs, nb_days] = [int(x) for x in source.readline().strip().split(' ')]
    scores = [int(x) for x in source.readline().strip().split(' ')]
    # centralize books in a dict
    books = {b_ide: Book(b_ide, score) for (b_ide, score) in enumerate(scores)}
    book_freqs = Counter()

    libs = []
    for l_ide in range(nb_libs):
        [l_nb_books, signup, ship] = [int(x) for x in source.readline().strip().split(' ')]
        lib = Library(l_ide, signup, ship)
        book_ids = [int(x) for x in source.readline().strip().split(' ')]
        book_freqs.update(book_ids)
        # lib.add_books([Book(b_ide, scores[b_ide]) for b_ide in book_ids])
        lib.add_books([books[b_ide] for b_ide in book_ids])
        libs.append(lib)

    sum_books = sum(book_freqs.values())

    for (b_ide, book) in books.items():
        book.frq = book_freqs[b_ide] / sum_books
    # for lib in libs:
    #     for book in lib.books:
    #         book.frq = book_freqs[book.ide] / sum_books

    return nb_books, nb_libs, nb_days, scores, libs, books
