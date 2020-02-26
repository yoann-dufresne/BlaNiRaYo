import sys
from collections import Counter
from src_2020.Library import Library, Book

def parse(source=None):
    if source is None:
        source = sys.stdin
    else:
        source = open(source)
    [nb_books, nb_lib, nb_days] = [int(x) for x in source.readline().strip().split(' ')]
    scores = [int(x) for x in source.readline().strip().split(' ')]
    book_freqs = Counter()

    books = [Book(i, scr) for i, scr in enumerate(scores)]

    libs = []
    for l_ide in range(nb_lib):
        [l_nb_books, signup, ship] = [int(x) for x in source.readline().strip().split(' ')]
        lib = Library(l_ide, signup, ship, books)
        book_idxs = [int(x) for x in source.readline().strip().split(' ')]
        book_freqs.update(book_idxs)
        lib.add_books([books[b_idx] for b_idx in book_idxs])
        libs.append(lib)

    sum_books = sum(book_freqs.values())
    for book in books:
        book.frq = book_freqs[book.ide] / sum_books

    return nb_days, books, libs
