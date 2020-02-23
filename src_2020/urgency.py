#!/usr/bin/env python3

import sys
from copy import deepcopy
from operator import attrgetter
from collections import Counter
from src_2020.Parser import parse, problem_stats
from src_2020.Parser import lib_sort_keys as sort_keys
from src_2020.Outputer import output


if __name__ == "__main__":
    if len(sys.argv) < 3:
        sys.stderr.write("Usage: cmd input_file output_file [attribute]\n")
        sys.stderr.write("attribute to be chosen among\n", ", ".join(sort_keys.keys()))
        sys.exit(1)
    if len(sys.argv) == 4:
        attrs = [sys.argv[3]]
    else:
        attrs = sort_keys.keys()
    problem_file = sys.argv[1]
    problem_stats(problem_file)
    best_score = 0
    best_sol = []
    best_avoid = None
    best_attr = None
    for attr in attrs:
        sort_key = sort_keys[attr]
        for do_rev in [False, True]:
            nb_books, nb_libs, nb_days, scores, libs, books = parse(problem_file)
            time_available = nb_days
            libs_order = []
            avoid = set()
            for lib in sorted(libs, key=sort_key, reverse=do_rev):
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
            this_score = sum(b.score for b in avoid)
            if do_rev:
                print(f"Solution rev sorting on {attr:15}: {this_score:>10}")
            else:
                print(f"Solution fwd sorting on {attr:15}: {this_score:>10}")
            if this_score > best_score:
                best_score = this_score
                best_sol = deepcopy(libs_order)
                best_avoid = avoid
                if do_rev:
                    best_attr = f"rev_{attr}"
                else:
                    best_attr = f"fwd_{attr}"
    max_score = sum(b.score for b in books.values())
    print(f"\nBest solution found sorting on {best_attr}")
    print(f"  Score: {best_score} / {max_score}")
    print(f"  Number of books scanned: {len(best_avoid)} / {nb_books}")
    print(f"  Number of libraries used: {len(best_sol)} / {nb_libs}")
    output(sys.argv[2], best_sol)
