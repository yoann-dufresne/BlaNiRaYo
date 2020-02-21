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

    libs = []
    for l_ide in range(nb_lib):
        [l_nb_books, signup, ship] = [int(x) for x in source.readline().strip().split(' ')]
        lib = Library(l_ide, signup, ship)
        book_ids = [int(x) for x in source.readline().strip().split(' ')]
        book_freqs.update(book_ids)
        lib.add_books([Book(b_ide, scores[b_ide]) for b_ide in book_ids])
        libs.append(lib)

    sum_books = sum(book_freqs.values())

    for lib in libs:
        for book in lib.books:
            book.frq = book_freqs[book.ide] / sum_books

    return nb_books, nb_lib, nb_days, scores, libs
