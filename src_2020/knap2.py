from src_2020.Parser import parse
from src_2020.Outputer import output
from src_2020.Scorer import scorer
from src_2020.Library import mask_books
import sys

if len(sys.argv) < 2:
    exit("args: input_file.txt")

prefix = sys.argv[1][sys.argv[1].index("_")-1]
nb_books, nb_lib, nb_days, scores, libs = parse(sys.argv[1])

from mip import Model, xsum, maximize, BINARY

L = list(range(len(libs)))
B = list(range(nb_books))
w = [libs[i].signup for i in L]

print("subscription times", w[:10])

m = Model('knap solver 2')
#m.verbose=0

l = [m.add_var(var_type=BINARY) for i in L]
b = [m.add_var(var_type=BINARY) for i in B]

#m.objective = maximize(xsum(p[i] * x[i] for i in I))
#m.objective = maximize(xsum(scores[i] * b[i] for i in B))
#m.objective = maximize(xsum(scores[i] * b[i] for i in B) + xsum(libs[i].signup * l[i] for i in L))

m += xsum(w[i] * l[i] for i in L) <= nb_days

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
    #print("book",bi,"libs",libs_having_book[bi])
    m += b[bi] <= xsum(l[li] for li in libs_having_book[bi])

#m.optimize(max_seconds=60)
m.optimize(max_seconds=60, relax=True)
#m.optimize(max_solutions=1,relax=True)
#m.optimize(max_solutions=100,relax=True)

libs_selected = [i for i in L if l[i].x >= 0.99]
books_selected = [i for i in B if b[i].x >= 0.99]
print(len(libs_selected),'selected libraries out of ',nb_lib)
print(len(books_selected),'selected books out of ',nb_books)

sol_filename = "res_2020/" +  prefix + "_sol.txt" 

libs = [libs[i] for i in libs_selected]

forbidden = set()
libs_sol = []
import heapq
lib_q = [(0,x) for x in libs]
def update_lib_queue():
    global lib_q
    remaining_libs = [lib for x,lib in lib_q]
    lib_q = []
    for lib in remaining_libs:
        heapq.heappush(lib_q, (-lib.interest2(nb_days, avoid=forbidden), lib))
iteration = 0
update_lib_queue()
while len(lib_q) > 0:
    if nb_lib < 10000 or iteration % 50 == 1:
        update_lib_queue()
    iteration += 1
    print(len(lib_q))
    value, max_lib = heapq.heappop(lib_q)
    #print(value,max_lib.worthy_books_first)
    libs_sol.append(max_lib)
    # Selection livres
    max_lib.books_to_scan = [x for x in mask_books(max_lib.worthy_books_first(nb_days), forbidden)]
    forbidden |= set(max_lib.books_to_scan)
    nb_days -= max_lib.signup

output(sol_filename, libs_sol)

score = scorer(sys.argv[1],sol_filename)
print("score",score)
