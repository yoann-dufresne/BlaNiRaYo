# maybe it will run but i never really maintained it as much as knap2.py
from src_2020.Parser import parse
from src_2020.Outputer import output
from src_2020.Scorer import scorer
from src_2020.Library import mask_books
import sys

if len(sys.argv) < 2:
    exit("args: input_file.txt")

prefix = sys.argv[1][sys.argv[1].index("_")-1]
nb_books, nb_lib, nb_days, scores, libs, books = parse(sys.argv[1])

from collections import defaultdict
libs_having_book = defaultdict(list)
for li in range(nb_lib):
    for book in libs[li].books:
        libs_having_book[book.ide] += [li]


from mip import Model, xsum, maximize, BINARY

L = list(range(len(libs)))
B = list(range(nb_books))
D = list(range(nb_days))
s = [libs[i].signup for i in L]

print("signup times", s[:10])

m = Model('knap solver 2')
#m.verbose=0

l = [m.add_var(var_type=BINARY) for i in L]
bd = [[m.add_var(var_type=BINARY) for d in D] for i in B] # book i is picked at day D

c = []
for i in L:
    c += [[m.add_var(var_type=BINARY) for d in D]] # 1 if library i had completed on day d

m.objective = maximize(xsum(scores[i] * b[i][d] for i in B for d in D))

m += xsum(s[i] * l[i] for i in L) <= nb_days

# book can only be picked by a library that owns it
for bi in B:
    #print("book",bi,"libs",libs_having_book[bi])
    m += xsum(b[bi][d] for d in D) <= xsum(l[li] for li in libs_having_book[bi])

# if library li1 is done at time t, then lib li1 needs to be done at time >= t+libs[li2].signup
for li1 in L:
    for li2 in L:
        if li1 == li2: continue
        continue
        m += xsum((t*c[li1][t] - t*c[li2][t]) for t in D) >= s[li2]

# only libs that are selected need to be done at a certain time
for li in L:
    m += xsum(c[li][t] for t in D) == l[li]

# when lib li is done at time t then it can only do a certain number of books
for li in L:
    time_needed = (len(libs[li].books) + libs[li].ship - 1) // libs[li].ship
    print("library",li,"needs time",time_needed,"out of",nb_days)
    # TODO stopped here but it doesn't work because some library just wont have time to do all their books
    #m += xsum((t*c[li][t]) for t in range(nb_days-s[li]-1) ) + time_needed <= nb_days 
    m += xsum((t*c[li][t]) for t in range(time_needed) ) + time_needed <= nb_days 

m.optimize(max_seconds=60)
#m.optimize(max_seconds=100, relax=True)
#m.optimize(max_solutions=1,relax=True)
#m.optimize(max_solutions=10,relax=True)

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
    max_books = self.nb_books_scannable(nb_days-max_lib.signup)
    max_lib.books_to_scan = [x for x in mask_books(max_lib.worthy_books_first(nb_days), forbidden)][:max_books]
    forbidden |= set(max_lib.books_to_scan)
    nb_days -= max_lib.signup

output(sol_filename, libs_sol)

score = scorer(sys.argv[1],sol_filename)
print("score",score)
