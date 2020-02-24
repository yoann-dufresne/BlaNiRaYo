# rationale:
# - de-duplicate books, one exemplaire in only one library
# - estimate payoff of libraries at each day

from src_2020.Parser import parse
from src_2020.Outputer import output
from src_2020.Scorer import scorer
from src_2020.Library import mask_books
from src_2020.Dedup import deduplicate_books 
import sys
import heapq
from copy import deepcopy
from collections import Counter

if len(sys.argv) < 2:
    exit("args: input_file.txt")

prefix = sys.argv[1][sys.argv[1].index("_")-1]
nb_books, nb_libs, nb_days, scores, libs, books = parse(sys.argv[1])

from statistics import mean, stdev, median
books_in_lib = [len(lib.books) for lib in libs]
print("books per lib before deduplication, mean %.2f / median %d / stdev %.2f / max %d / min %d" \
        %(mean(books_in_lib),median(books_in_lib),stdev(books_in_lib),max(books_in_lib),min(books_in_lib)))

libs = deduplicate_books(libs)
#libs = smooth_books(libs)
books_in_lib = [len(lib.books) for lib in libs]
print("books per lib after deduplication, mean %.2f / median %d / stdev %.2f / max %d / min %d"% \
        (mean(books_in_lib),median(books_in_lib),stdev(books_in_lib),max(books_in_lib),min(books_in_lib)))

booksc=Counter()
for lib in libs:
    for book in lib.books:
        booksc[book.ide] += 1
print("sanity check: average frequency of a book",sum([booksc[b] for b in books]) / len(books)) 

# now that all books are distinct, we can calculate exactly the payoff of a library if chosen at a certain timepoint
payoff = dict()
for lib in libs:
    for day in range(nb_days):
        lib.signed = False
        payoff[(lib.ide,day)] = sum([b.score for b in lib.books_by_worth(
                time_available=nb_days-day)])
 
L = [lib.ide for lib in libs] # not always range(libs) if we deleted some before
D = list(range(nb_days)) 

do_mip = "--use_saved_mip" not in sys.argv
if do_mip:
    from mip import Model, xsum, maximize, BINARY

    w = [libs[i].signup for i in L]

    print("subscription times", w[:10])

    m = Model('knap solver 3')
    #m.verbose=0

    l = dict()
    o = dict() # occuped by signup
    for i in L:
        for d in D:
            l[(i,d)] = m.add_var(var_type=BINARY)
            o[(i,d)] = m.add_var(var_type=BINARY)

    # maximize payoff of selected libs
    m.objective = maximize(xsum(payoff[(i,d)] * l[(i,d)] for i in L for d in D))

    # under constraint that selected libs have a signup time
    m += xsum(w[i] * l[(i,d)] for i in L for d in D) <= nb_days
    # i suspect this constraint is redundant

    # lib can be signed up only once
    for i in L:
        m += xsum(l[(i,d)] for d in D) <= 1

    # if a lib is signed up at a certain time, we're occupied during the next days
    for i in L:
        if i % 100 == 0: print(i)
        for d in D:
            """ # for some reason seems to hurt mip resolution
            signup_range = min(nb_days,d+libs[i].signup) - d
            m += signup_range * l[(i,d)] <= xsum(o[(i,d+k)] for k in range(signup_range))
            """
            #"""
            for k in range(libs[i].signup):
                if d+k >= nb_days: continue
                m += l[(i,d)] <= o[(i,d+k)]
            #"""


    # at each day, we can only be occupied by signing up a single library
    for d in D:
        m += xsum(o[(i,d)] for i in L) <= 1

    m.optimize()

    libs_selected = set([(i,d) for i in L for d in D if l[(i,d)].x >= 0.99])

    save=True
    if save:
        f=open(prefix+"_knap3_mip_libs.txt","w")
        f.write(str(libs_selected))
        f.close()
else:
    libs_selected=eval(open(prefix+"_knap3_mip_libs.txt").read().strip())

print(len(libs_selected), 'selected libraries out of ', len(libs))
print(sum([libs[i].signup for (i,d) in libs_selected]), 'total signup time out of', nb_days,'days')

sol_filename = "res_2020/" +  prefix + "_sol.txt" 

libs_sol = []
avoid = set()
for d in D:
    for i in L:
        if (i,d) not in libs_selected: continue
        libs[i].signed = False
        books_to_scan = libs[i].books_by_worth(
                time_available=nb_days-d,
                avoid=avoid)
        libs[i].books_to_scan = books_to_scan
        libs_sol.append(libs[i])
        avoid |= set(books_to_scan)
        libs[i].signed = True 

output(sol_filename, libs_sol)

score = scorer(sys.argv[1],sol_filename)
print("score",score)
