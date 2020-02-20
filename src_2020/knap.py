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

w = [libs[i].signup for i in range(len(libs))]
p = [1 for i in range(len(libs))]  # dummy interest score
p = [libs[i].interest1(nb_days) for i in range(len(libs))]
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
print(len(selected),'selected items out of ',nb_lib)#': {}'.format(selected))

sol_filename = "../res_2020/" +  prefix + "_sol.txt" 


#score = scorer(sys.argv[1],"../res_2020/" + sol_filename)
#print("score",score)
libs = [libs[i] for i in selected]

forbidden = set()
libs.sort(key=lambda x: x.interest1(nb_days, avoid=forbidden))
for lib in libs:
    # Selection livres-
    lib.books_to_scan = [x for x in mask_books(lib.worthy_books_first, forbidden)]
    forbidden |= set(lib.books_to_scan)

output("res_2020/sol.txt", libs)
