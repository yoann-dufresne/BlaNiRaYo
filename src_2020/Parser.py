import sys
from src_2020.Library import Library, Book

def parse(source=None):
    if source is None:
        source = sys.stdin
    else:
        source = open(source)
    nb_books, nb_lib, nb_days = [int(x) for x in source.readline().strip().split(' ')]
    scores = [int(x) for x in source.readline().strip().split(' ')]

    libs = []
    for l in range(nb_lib):
        lib_values = [int(x) for x in source.readline().strip().split(' ')]
        lib = Library(l, lib_values[1], lib_values[2])
        books = [Book(int(x), scores[int(x)]) for x in source.readline().strip().split(' ')]
        libs.append(lib)

    return nb_books, nb_lib, nb_days, scores, libs



