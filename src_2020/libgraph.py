#!/usr/bin/env python3

import sys
from copy import deepcopy
from operator import attrgetter
from collections import Counter
from itertools import combinations
import numpy as np
import pandas as pd
import networkx as nx
from src_2020.Parser import parse, problem_stats
from src_2020.Parser import lib_sort_keys as sort_keys
from src_2020.Outputer import output

# TODO: graph of libraries based on book content similarity
# partition graph
# select one representative library per component

# Book choice criteria
bk_quals = ["frq", "inv_frq", "score", "weighted_score"]
book_selectors = {
    bk_qual: attrgetter(bk_qual)
    for bk_qual in bk_quals}


def make_nbscan_getter(time_avail, avoid):
    def get_nbscannable(lib):
        return max(
            lib.nb_books_scannable(time_avail),
            sum(1 for book in lib.books if book not in avoid))
    return get_nbscannable


# TODO: test dists relative to libs sizes (smallest of the 2?)
def bk_dist(lib1, lib2):
    return len(set(lib1.books) & set(lib2.books))


def build_libgraph(libs):
    libgraph = nx.Graph()
    libgraph.add_nodes_from(libs)
    for (lib1, lib2) in combinations(libs, 2):
        libgraph.add_edge(lib1, lib2, weight=bk_dist(lib1, lib2))
    return libgraph


def cut_libgraph(libgraph, cut_dist):
    def edge_filter(lib1, lib2):
        return libgraph[lib1][lib2].get("weight", 0) > cut_dist
    return nx.subgraph_view(libgraph, filter_edge=edge_filter)


get_urgency = sort_keys["urgency"]
get_libworth = sort_keys["libworth"]

def get_best_lib(libs, sort_key=get_libworth, do_rev=True):
    """By default, get the library with the highest total book score."""
    return sorted(libs, key=sort_key, reverse=do_rev)[0]


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
    lib_stats = problem_stats(problem_file)
    #####################################################
    # Pre-select a possibly diverse subset of libraries #
    #####################################################
    nb_books, nb_libs, nb_days, scores, all_libs, books = parse(problem_file)
    # Minimum number of library groups we want to separate
    # TODO: Optimize this
    # min_nb_groups = 10
    # min_nb_groups = 10 * nb_days // lib_stats["daysneed"]
    min_nb_groups = nb_days // lib_stats["daysneed"]
    libgraph = build_libgraph(all_libs)
    lib_dists = np.fromiter(
        (data["weight"] for (_, _, data) in libgraph.edges(data=True)),
        dtype=int)
    dist_quantiles = np.quantile(
        lib_dists, np.linspace(0, 1, 100), interpolation="higher")
    # interpolation="higher" may give duplicate values but
    # we use it because we only need to cut on existing lib distances
    # TODO: should we go down instead, and loop until we have less than min_nb_groups?
    # (If so, don't cut from already cutted graph)
    for cut_dist in sorted(set(dist_quantiles)):
        libgraph = cut_libgraph(libgraph, cut_dist)
        lib_sets = list(nx.connected_components(libgraph))
        if len(lib_sets) > min_nb_groups:
            break
    print(f"Partitioned the libraries into", len(lib_sets), "sets")
    # libs = list(map(get_best_lib, lib_sets))
    ############################
    # Order selected libraries #
    ############################
    best_score = 0
    best_sol = []
    best_avoid = None
    best_attr = None
    best_selection = None
    for selecter_attr in attrs:
        selecter = sort_keys[selecter_attr]
        for do_rev1 in [False, True]:
            if do_rev1:
                selection_name = f"rev_{selecter_attr}"
            else:
                selection_name = f"fwd_{selecter_attr}"
            print(f"Selecting best libs on {selection_name}")
            libs = [get_best_lib(lib_set, sort_key=selecter, do_rev=do_rev1) for lib_set in lib_sets]
            for attr in attrs:
                sort_key = sort_keys[attr]
                for do_rev in [False, True]:
                    for lib in libs:  # reset the libs
                        lib.signed = False
                        lib.books_to_scan = []
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
                    if time_available:
                        # TODO: improve this to select missing worthy books
                        # Try to add some libraries from (all_libs - libs_order) with low urgency
                        for lib in sorted(set(all_libs) - set(libs_order), key=sort_key, reverse=do_rev):
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
                        best_selection = selection_name
                        best_score = this_score
                        best_sol = deepcopy(libs_order)
                        best_avoid = avoid
                        if do_rev:
                            best_attr = f"rev_{attr}"
                        else:
                            best_attr = f"fwd_{attr}"
    max_score = sum(b.score for b in books.values())
    print(f"\nBest solution found selecting on {selection_name} and sorting on {best_attr}")
    print(f"  Score: {best_score} / {max_score}")
    print(f"  Number of books scanned: {len(best_avoid)} / {nb_books}")
    print(f"  Number of libraries used: {len(best_sol)} / {nb_libs}")
    output(sys.argv[2], best_sol)
