import sys
from collections import Counter
from operator import attrgetter
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


lib_sort_attrs = ["ship", "signup", "urgency", "libsize", "libworth", "daysneed", "urginvworth","testing"]
lib_sort_keys = {
    attr: attrgetter(attr)
    for attr in lib_sort_attrs}


def problem_stats(problem_file):
    nb_books, nb_libs, nb_days, scores, libs, books = parse(problem_file)
    time_available = nb_days
    scores_counter = Counter(scores)
    counters = {
        attr: Counter(map(lib_sort_keys[attr], libs))
        for attr in lib_sort_attrs}
    print(f"Problem {sys.argv[1]}")
    print(f"  Number of books: {nb_books}")
    print(f"  Number of distinct scores: {len(scores_counter)}")
    print(f"  Number of libraries: {nb_libs}")
    print(f"  Number of days: {nb_days}")
    for attr in lib_sort_attrs:
        if len(counters[attr]) <= 20:
            info = ", ".join(map(str, sorted(counters[attr].keys())))
        else:
            info = f"{min(counters[attr].keys())} -> {max(counters[attr].keys())}"
        print(f"  Number of distinct values for {attr}: {len(counters[attr])} ({info})")
