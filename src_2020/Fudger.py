#!/usr/bin/env python3

import sys
from copy import deepcopy
from operator import attrgetter
from collections import Counter
from src_2020.Parser import parse
from src_2020.Outputer import output
from src_2020.Library import Library 
from src_2020.Scorer import scorer 
import random
import copy

def solution_read(solution_file, libs):
    nb_libraries = None
    sol_libs = []
    current_lib = None
    day = 0
    for i, line in enumerate(open(solution_file).read().split('\n')):
        if len(line.strip()) == 0: break
        if i == 0:
            nb_libraries = int(line)
            continue
        if i%2 == 1:
            library_id, nb_books = map(int,line.strip().split())
            current_lib = copy.copy(libs[library_id])
        else:
            lib_books = list(map(int,line.strip().split()))
            current_lib.books_to_scan = lib_books
            current_lib.signup_on = day
            sol_libs += [current_lib]
            day += libs[library_id].signup
    assert day == sum([sol_lib.signup for sol_lib in sol_libs]), (day,"!=",sum([sol_lib.signup for sol_lib in sol_libs]))
    return sol_libs, day

def solution_score(libs,scores):
    all_books = set()
    for lib in libs:
        all_books |= set(lib.books_to_scan)
    total_score = 0
    for book in all_books:
        total_score += scores[book]
    return total_score

def solution_replace_lib(sol_libs, i, lib, nb_days):
    # avoid all other books from the solution
    avoid = set([x for j in range(len(sol_libs)) for x in sol_libs[j].books_to_scan if j != i ])
    time_available = nb_days - (sol_libs[i].signup_on + sol_libs[i].signup)
    new_sol = copy.copy(sol_libs) # gotta copy
    new_sol[i] = copy.copy(lib)
    new_sol[i].signup_on = sol_libs[i].signup_on
    lib.signed = True # to avoid books_by_worth adjust time_available
    new_sol[i].books_to_scan =  [book.ide for book in lib.books_by_worth(avoid=avoid, time_available=time_available)]
    new_sol[i].signed = True 
    return new_sol

if __name__ == "__main__":
    if len(sys.argv) < 4:
        sys.stderr.write("Usage: cmd input_file solution_file output_file\n")
        sys.exit(1)
    
    problem_file = sys.argv[1]
    nb_books, nb_libs, nb_days, scores, libs, books = parse(problem_file)

    solution_file = sys.argv[2]
    output_file = sys.argv[3]
    sol_libs, sol_days = solution_read(solution_file,libs) 
    old_score = solution_score(sol_libs,scores)
    
    print("original solution, computing its score..")
    scorer(problem_file,solution_file)

    while True:
        # randomly replace a library by another one
        i = random.randint(0,len(sol_libs)-1)
        other_libs_ids = list(set(range(len(libs))) - set([sol_libs[i].ide for i in range(len(sol_libs))]))
        #nb_sol_days = sum([lib.signup for lib in sol_libs])
        #buffer_days = nb_days - nb_sol_days # i tried to allow longerl libs, but i realized later that it shifts everything after
        new_lib = libs[random.choice(other_libs_ids)]
        if new_lib.signup > sol_libs[i].signup: 
            #print("new lib has higher signup time..", sol_libs[i].signup, lib.signup)
            # TODO could see how many signup days are actually left
            continue
        new_sol_libs = solution_replace_lib(sol_libs, i, new_lib, nb_days)
        new_score = solution_score(new_sol_libs,scores)
        if new_score > old_score:
            print("!new best (%d)" %new_score)
            old_score = new_score
            sol_libs = copy.copy(new_sol_libs)
            output(output_file, sol_libs)
            print("confirming score..")
            scorer(problem_file,output_file)
