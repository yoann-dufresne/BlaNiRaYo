# back from the roots! knap.py but this time with lib intersection penalty


from src_2020.Parser import parse
from src_2020.Outputer import output
from src_2020.Scorer import scorer
from src_2020.Library import mask_books
from src_2020.IntersectLibs import intersect_libs 
import sys
from copy import deepcopy

if len(sys.argv) < 2:
    exit("args: input_file.txt")

prefix = sys.argv[1][sys.argv[1].index("_")-1]
sol_filename = "res_2020/" +  prefix + "_sol.txt" 

nb_books, nb_libs, nb_days, scores, libs, books = parse(sys.argv[1])

# remove some libs and reorder libs
remove_some_libs = True
if remove_some_libs:
    remember_lib_ide = dict()
    libs = [lib for lib in libs if len(lib.books) >= 7]
    for i,lib in enumerate(libs):
        remember_lib_ide[i] = lib.ide
        lib.ide = i
    nb_libs = len(libs)
    print("number of libs now:",nb_libs)

from mip import Model, xsum, maximize, BINARY, INTEGER

L = list(range(len(libs)))

intersections = intersect_libs(libs)

m = Model('knap solver 7')
#m.verbose=0

w = [libs[i].signup for i in L]
x = [m.add_var(var_type=BINARY) for i in L]

print("adding intersection constraints")
xinter = dict()
for n,(i,j) in enumerate(intersections):
    if n % 100000 == 0: print(n)
    xinter[(i,j)] = m.add_var(var_type=BINARY)
    m += xinter[(i,j)] >= x[i] + x[j] - 1 # a trick to do a binary AND

penalty = m.add_var(var_type=INTEGER)

m += penalty == xsum(65*xinter[(i,j)]*intersections[(i,j)]/2 for (i,j) in intersections)

m.objective = maximize(xsum(libs[i].libworth * x[i] for i in L) - penalty)

m += xsum(w[i] * x[i] for i in L) <= nb_days

print("done adding constraints")

m.optimize()

selected = [i for i in L if x[i].x >= 0.99]
print(len(selected), 'selected items out of ', nb_libs)  #': {}'.format(selected))

libs = [libs[i] for i in selected]

avoid = set()
libs_sol = []
time_available = nb_days
for max_lib in libs:
    # Selection livres
    max_lib.signed = False 
    books_to_scan = max_lib.books_by_worth(
                    time_available=time_available,
                    avoid=avoid)
    max_lib.books_to_scan = books_to_scan
    max_lib.signed = True
    if len(max_lib.books_to_scan) == 0: continue # avoid outputting an empty lib
    libs_sol.append(max_lib)
    avoid |= set(books_to_scan)
    time_available -= max_lib.signup
    if time_available <= 0:
        break

if remove_some_libs:
    # fix lib identifiers (as we may have deleted some libs)
    for lib in libs_sol:
        lib.ide = remember_lib_ide[lib.ide]

output(sol_filename, libs_sol)

score = scorer(sys.argv[1],sol_filename)
print("score",score)
