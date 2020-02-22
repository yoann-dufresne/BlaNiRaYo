#!/usr/bin/env python3

import sys
from copy import deepcopy
from operator import attrgetter
from collections import Counter
from src_2020.Parser import parse
from src_2020.Outputer import output

sort_attrs = ["ship", "signup", "urgency", "libsize", "libworth"]
# get_ship = attrgetter("ship")
# get_signup = attrgetter("signup")
# get_urgency = attrgetter("urgency")
# get_libsize = attrgetter("libsize")
# get_libworth = attrgetter("libworth")
sort_keys = {
    attr: attrgetter(attr)
    for attr in sort_attrs}


def problem_stats(problem_file):
    nb_books, nb_libs, nb_days, scores, libs, books = parse(problem_file)
    time_available = nb_days
    scores_counter = Counter(scores)
    counters = {
        attr: Counter(map(sort_keys[attr], libs))
        for attr in sort_attrs}
    print(f"Problem {sys.argv[1]}")
    print(f"  Number of books: {nb_books}")
    print(f"  Number of distinct scores: {len(scores_counter)}")
    print(f"  Number of libraries: {nb_libs}")
    print(f"  Number of days: {nb_days}")
    for attr in sort_attrs:
        if len(counters[attr]) <= 20:
            info = ", ".join(map(str, sorted(counters[attr].keys())))
        else:
            info = f"{min(counters[attr].keys())} -> {max(counters[attr].keys())}"
        print(f"  Number of distinct values for {attr}: {len(counters[attr])} ({info})")
    # ships = Counter(map(get_ship, libs))
    # signups = Counter(map(get_signup, libs))
    # urgencies = Counter(map(get_urgency, libs))
    # libsizes = Counter(map(get_libsize, libs))
    # libworths = Counter(map(get_libworth, libs))
    # if len(libsizes) <= 20:
    #     info = ", ".join(map(str, sorted(libsizes.keys())))
    # else:
    #     info = f"{min(libsizes.keys())} -> {max(libsizes.keys())}"
    # print(f"  Number of distinct library sizes: {len(libsizes)} ({info})")
    # if len(ships) <= 20:
    #     info = ", ".join(map(str, sorted(ships.keys())))
    # else:
    #     info = f"{min(ships.keys())} -> {max(ships.keys())}"
    # print(f"  Number of distinct ships: {len(ships)} ({info})")
    # if len(signups) <= 20:
    #     info = ", ".join(map(str, sorted(signups.keys())))
    # else:
    #     info = f"{min(signups.keys())} -> {max(signups.keys())}"
    # print(f"  Number of distinct signups: {len(signups)} ({info})")
    # if len(libworths) <= 20:
    #     info = ", ".join(map(str, sorted(libworths.keys())))
    # else:
    #     info = f"{min(libworths.keys())} -> {max(libworths.keys())}"
    # print(f"  Number of distinct libworths: {len(libworths)} ({info})")
    # if len(urgencies) <= 20:
    #     info = ", ".join(map(str, sorted(urgencies.keys())))
    # else:
    #     info = f"{min(urgencies.keys())} -> {max(urgencies.keys())}"
    # print(f"  Number of distinct urgencies: {len(urgencies)} ({info})")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        sys.stderr.write("Usage: cmd input_file output_file [attribute]\n")
        sys.stderr.write("attribute to be chosen among\n", ", ".join(sort_attrs))
        sys.exit(1)
    if len(sys.argv) == 4:
        attrs = [sys.argv[3]]
    else:
        attrs = sort_attrs
    problem_file = sys.argv[1]
    problem_stats(problem_file)
    # TODO: Why are there side effects (quick score decrease in the loop over attrs)?
    best_score = 0
    best_sol = []
    best_avoid = None
    best_attr = None
    for attr in attrs:
        sort_key = sort_keys[attr]
        nb_books, nb_libs, nb_days, scores, libs, books = parse(problem_file)
        time_available = nb_days
        # these_libs = deepcopy(libs)
        libs_order = []
        avoid = set()
        for lib in sorted(libs, key=sort_key):
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
        print(f"Solution sorting on {attr}: {this_score}")
        if this_score > best_score:
            best_score = this_score
            best_sol = deepcopy(libs_order)
            best_avoid = avoid
            best_attr = attr
    max_score = sum(b.score for b in books.values())
    print(f"\nBest solution found sorting on {best_attr}")
    print(f"  Score: {best_score} / {max_score}")
    print(f"  Number of books scanned: {len(best_avoid)} / {nb_books}")
    print(f"  Number of libraries used: {len(best_sol)} / {nb_libs}")
    output(sys.argv[2], best_sol)
