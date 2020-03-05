# now we're taking a different route for instance d
# we know we have 100000 books total and can fit 15000 libraries in the solution
# let's just encode that in the MIP; so in a way it's similar to knap2.py


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
    libs = [lib for lib in libs if len(lib.books) >= 5]
    for i,lib in enumerate(libs):
        remember_lib_ide[i] = lib.ide
        lib.ide = i
    nb_libs = len(libs)
    print("number of libs now:",nb_libs)

from mip import Model, xsum, maximize, BINARY, INTEGER

L = list(range(len(libs)))
B = list(range(nb_books))

intersections = intersect_libs(libs)

m = Model('knap solver 8')
#m.verbose=0

w = [libs[i].signup for i in L]
l = [m.add_var(var_type=BINARY) for i in L]
b = [m.add_var(var_type=BINARY) for i in B]

#m.objective = maximize(xsum(b[i] for i in B)) 
m += xsum(b[i] for i in B) >= 78000 # don't bother outputting solutions less than 5.070M

m += xsum(l[i] for i in L) <= 15000

for li in L:
    for bib in libs[li].books: 
        bi = bib.ide
        m += b[bi] >= l[li]

from collections import defaultdict
libs_having_book = defaultdict(list)
for li in L:
    for book in libs[li].books:
        libs_having_book[book.ide] += [li]

for bi in B:
    m += b[bi] <= xsum(l[li] for li in libs_having_book[bi])


print("done adding constraints")

m.optimize()

selected = [i for i in L if l[i].x >= 0.99]
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
