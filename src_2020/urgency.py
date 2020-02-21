#!/usr/bin/env python3

import sys
from operator import attrgetter
from itertools import combinations
from random import choice
import networkx as nx
from src_2020.Parser import parse
from src_2020.Library import mask_books, Book
from src_2020.Outputer import output


get_score = attrgetter("score")
get_urgency = attrgetter("urgency")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.stderr.write("Usage: cmd input_file output_file\n")
        sys.exit(1)
    nb_books, nb_libs, nb_days, scores, libs, books = parse(sys.argv[1])
    time_available = nb_days
    print(f"Number of books: {nb_books}")
    print(f"Number of libraries: {nb_libs}")
    libs_order = []
    avoid = set()
    for lib in sorted(libs, key=get_urgency):
        books_to_scan = lib.books_by_worth(
            time_available=time_available,
            avoid=avoid)
        if books_to_scan:
            lib.books_to_scan.extend(books_to_scan)
            lib.signed = True
            avoid |= set(books_to_scan)
            libs_order.append(lib)
            time_available -= lib.signup
            if time_available <= 0:
                break
    output(sys.argv[2], libs_order)
