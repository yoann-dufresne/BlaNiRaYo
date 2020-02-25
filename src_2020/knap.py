from src_2020.Parser import parse
from src_2020.Outputer import output
from src_2020.Scorer import scorer
from src_2020.Library import mask_books
import sys
from copy import deepcopy

if len(sys.argv) < 2:
    exit("args: input_file.txt")

prefix = sys.argv[1][sys.argv[1].index("_")-1]
sol_filename = "res_2020/" +  prefix + "_sol.txt" 

nb_books, nb_libs, nb_days, scores, libs, books = parse(sys.argv[1])

from mip import Model, xsum, maximize, BINARY

weights = {
'dummy': [1 for i in range(len(libs))],  # dummy weights
'interest1': [libs[i].interest1(nb_days) for i in range(len(libs))],
'libworth': [libs[i].libworth for i in range(len(libs))],
'1/urginvworth': [1.0/libs[i].urginvworth for i in range(len(libs))],
'1/urgency':  [1.0/libs[i].urgency for i in range(len(libs))],
'libsize': [libs[i].libsize for i in range(len(libs))],
'1/signup': [1.0/libs[i].signup for i in range(len(libs))],
'signup': [libs[i].signup for i in range(len(libs))]
}

best_score = 0
best_sol = []
best_weight = None

def execute(metric):
    global best_score, best_sol, best_weight

    nb_books, nb_libs, nb_days, scores, libs, books = parse(sys.argv[1])
    I = list(range(len(libs)))

    m = Model('knap solver 1')
    m.verbose=0

    w = [libs[i].signup for i in range(len(libs))]
    p = weights[metric]
    x = [m.add_var(var_type=BINARY) for i in I]

    #print("subscription times", w[:10])
    #print("interest", p[:10])

    m.objective = maximize(xsum(p[i] * x[i] for i in I))

    m += xsum(w[i] * x[i] for i in I) <= nb_days

    m.optimize()

    selected = [i for i in I if x[i].x >= 0.99]
    print(len(selected), 'selected items out of ', nb_libs)  #': {}'.format(selected))

    libs = [libs[i] for i in selected]

    avoid = set()
    libs_sol = []
    import heapq
    lib_q = [(0,x) for x in libs]
    def update_lib_queue():
        nonlocal lib_q
        remaining_libs = [lib for x,lib in lib_q]
        lib_q = []
        for lib in remaining_libs:
            heapq.heappush(lib_q, (-lib.interest1(nb_days, avoid=avoid), lib))
    iteration = 0
    update_lib_queue()
    time_available = nb_days
    while len(lib_q) > 0:
        if nb_libs < 10000 or iteration % 50 == 1:
            update_lib_queue()
        iteration += 1
        value, max_lib = heapq.heappop(lib_q)
        libs_sol.append(max_lib)
        # Selection livres
        nb_days -= max_lib.signup
        books_to_scan = max_lib.books_by_worth(
                        time_available=nb_days,
                        avoid=avoid)
        max_lib.books_to_scan = books_to_scan
        max_lib.signed = True
        avoid |= set(books_to_scan)
        time_available -= max_lib.signup
        if time_available <= 0:
            break
    this_score = sum(b.score for b in avoid)
    if this_score  > best_score:
        best_score = this_score
        best_sol = deepcopy(libs_sol)
        best_weight = metric
    print("score with MIP optimizing total '%s' of libraries" % metric,this_score)

for metric in weights:
    execute(metric)

print(f"\nBest solution found sorting on {best_weight}")
print(f"  Score: {best_score}")
print(f"  Number of books scanned: {sum([len(lib.books) for lib in best_sol])} / {nb_books}")
print(f"  Number of libraries used: {len(best_sol)} / {nb_libs}")
output(sol_filename, best_sol)
