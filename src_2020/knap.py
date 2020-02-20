from src_2020.Parser import parse
from src_2020.Outputer import output
import sys


nb_books, nb_lib, nb_days, scores, libs = parse(sys.argv[1])

from mip import Model, xsum, maximize, BINARY

w = [libs[i].ship for i in range(len(libs))]
p = [1 for i in range(len(libs))] # libs[i].interest1(nb_days) for i in range(len(libs))]
I = list(range(len(libs)))

print("subscription times", w[:10])
print("interest", p[:10])

m = Model('knap solver 2')
m.verbose=0

x = [m.add_var(var_type=BINARY) for i in I]

m.objective = maximize(xsum(p[i] * x[i] for i in I))

m += xsum(w[i] * x[i] for i in I) <= nb_days

m.optimize()

selected = [i for i in I if x[i].x >= 0.99]
print(len(selected),'selected items out of ',nb_lib)#': {}'.format(selected))

output("sol.txt",[libs[i] for i in selected])
