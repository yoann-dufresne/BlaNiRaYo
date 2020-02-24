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
from itertools import combinations
#random.seed(17)

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

def solution_replace_lib(sol_libs, i, lib, nb_days, last_interval_index):
    # avoid all other books from the solution
    avoid = set([x for j in range(len(sol_libs)) for x in sol_libs[j].books_to_scan if j != i ])
    new_sol = copy.copy(sol_libs) # gotta have a copy 
    new_sol[i] = copy.copy(lib)
    # update new signup_on times (everything may be shifted)
    for j in range(len(sol_libs)): # for some reason if I compute only from range(i,..) it messes up the solution!
        if j > 0:
            new_sol[j].signup_on = new_sol[j-1].signup_on + new_sol[j-1].signup 
        else:
            new_sol[0].signup_on = 0
    time_available = nb_days - (new_sol[i].signup_on + new_sol[i].signup)
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

    tentatives = 0
    while True:
        # randomly replace k libraries by other ones
        k=1 # k>1 isn't guaranteed to be bugfree and actually doesnt seem to be that effective
        # select an interval (start_index,start_index+k) within the solution
        start_index = random.randint(0,len(sol_libs)-k)
        # compute total signup time within that interval
        total_signup = sum([sol_libs[start_index+j].signup for j in range(k)]) 
        # see which libraries are already used in the solution
        already_used_libs = set([sol_libs[i].ide for i in range(len(sol_libs))])
        # get a list of possible replacements from the original library list (minus those already used)
        # caveat: so, a possible replacement has zero intersection with libs of the existing solution
        possible_replacements = combinations(set(range(len(libs))) - already_used_libs,k)
        sys.stdout.write('\r attempt: %d' %tentatives)
        sys.stdout.flush()
        tentatives+=1
        #possible_replacement = random.choice(list(possible_replacements))
        #if True:
        for possible_replacement in possible_replacements:
            # estimate the total signup time of the replacement before proceeding
            repl_total_signup = sum([libs[j].signup for j in possible_replacement])
            if repl_total_signup > total_signup:
                continue
            #at this point we know that the new libraries won't take more time than the ones in the previous interval
            #so let's replace the old ones with the new ones in the solution.
            new_sol_libs = copy.copy(sol_libs)
            for i,selected in enumerate(possible_replacement):
                new_lib = libs[selected]
                new_sol_libs = solution_replace_lib(new_sol_libs, start_index+i, new_lib, nb_days, start_index+k)
            # evaluate new solution score
            new_score = solution_score(new_sol_libs,scores)
            if new_score > old_score:
                print("!new best (%d)" %new_score,"by replacing",set(range(start_index,start_index+k)))
                old_score = new_score
                sol_libs = copy.copy(new_sol_libs)
                output(output_file, sol_libs)
                print("confirming score..")
                scorer(problem_file,output_file)
            #break
