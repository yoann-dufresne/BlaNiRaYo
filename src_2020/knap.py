from src_2020.Parser import parse
from src_2020.Outputer import output
from src_2020.Scorer import scorer
from src_2020.Library import mask_books
import sys

if len(sys.argv) < 2:
    exit("args: input_file.txt")

prefix = sys.argv[1][sys.argv[1].index("_")-1]
nb_books, nb_lib, nb_days, scores, libs, books = parse(sys.argv[1])

from mip import Model, xsum, maximize, BINARY

w = [libs[i].signup for i in range(len(libs))]
# p = [1 for i in range(len(libs))]  # dummy interest score
#p = [libs[i].interest1(nb_days) for i in range(len(libs))]
p = [1.0/libs[i].urgency for i in range(len(libs))]
I = list(range(len(libs)))

print("subscription times", w[:10])
print("interest", p[:10])

m = Model('knap solver 1')
m.verbose=0

x = [m.add_var(var_type=BINARY) for i in I]

m.objective = maximize(xsum(p[i] * x[i] for i in I))

m += xsum(w[i] * x[i] for i in I) <= nb_days

m.optimize()

selected = [i for i in I if x[i].x >= 0.99]
print(len(selected), 'selected items out of ', nb_lib)  #': {}'.format(selected))

sol_filename = "res_2020/" +  prefix + "_sol.txt" 

libs = [libs[i] for i in selected]

forbidden = set()
libs_sol = []
import heapq
lib_q = [(0,x) for x in libs]
def update_lib_queue():
    global lib_q
    remaining_libs = [lib for x,lib in lib_q]
    lib_q = []
    for lib in remaining_libs:
        heapq.heappush(lib_q, (-lib.interest1(nb_days, avoid=forbidden), lib))
        #heapq.heappush(lib_q, (lib.urgency, lib))
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
    nb_days -= max_lib.signup
    max_lib.books_to_scan = [x for x in mask_books(max_lib.worthy_books_first(nb_days), forbidden)]
    forbidden |= set(max_lib.books_to_scan)

output(sol_filename, libs_sol)

score = scorer(sys.argv[1],sol_filename)
print("score",score)
