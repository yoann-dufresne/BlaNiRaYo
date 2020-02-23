from src_2020.Parser import parse
from src_2020.Outputer import output
from src_2020.Scorer import scorer
from src_2020.Library import mask_books
import sys

if len(sys.argv) < 2:
    exit("args: input_file.txt")

prefix = sys.argv[1][sys.argv[1].index("_")-1]
nb_books, nb_libs, nb_days, scores, libs, books = parse(sys.argv[1])

do_mip = "--use_saved_mip" not in sys.argv
if do_mip:
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
    m.objective = maximize(xsum(scores[i] * b[i] for i in B))
    #m.objective = maximize(xsum(scores[i] * b[i] for i in B) + 1000*xsum(-libs[i].signup * l[i] for i in L))

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
    #m.optimize(max_seconds=100, relax=True)
    #m.optimize(max_solutions=1,relax=True)
    #m.optimize(max_solutions=10,relax=True)
    #m.optimize(max_solutions=100,relax=True)
    m.optimize()

    libs_selected = [i for i in L if l[i].x >= 0.99]
    books_selected = [i for i in B if b[i].x >= 0.99]

    save=True
    if save:
        f=open(prefix+"_knap2_mip_libs.txt","w")
        f.write(str(libs_selected))
        f.close()
        f=open(prefix+"_knap2_mip_books.txt","w")
        f.write(str(books_selected))
        f.close()

else:
    libs_selected=eval(open(prefix+"_knap2_mip_libs.txt").read().strip())
    books_selected=eval(open(prefix+"_knap2_mip_books.txt").read().strip())

print(len(libs_selected), 'selected libraries out of ', nb_libs)
print(sum([libs[i].signup for i in libs_selected]), 'total signup time out of', nb_days,'days')
print(len(books_selected), 'selected books out of ', nb_books)
libs = [libs[i] for i in libs_selected]
sol_filename = "res_2020/" +  prefix + "_sol.txt" 

avoid = set()
libs_sol = []
import heapq
lib_q = [(0,lib) for lib in libs]
time_available = nb_days
def update_lib_queue():
    global lib_q, time_available
    remaining_libs = [lib for x,lib in lib_q]
    lib_q = []
    for lib in remaining_libs:
        #heapq.heappush(lib_q, (lib.interest1(time_available, avoid=avoid), lib))
        #heapq.heappush(lib_q, (lib.urgency, lib))
        heapq.heappush(lib_q, (lib.urginvworth, lib))
iteration = 0
update_lib_queue()
while len(lib_q) > 0:
    if nb_libs < 10000 or iteration % 50 == 1:
        update_lib_queue()
    iteration += 1
    print(len(lib_q))
    value, max_lib = heapq.heappop(lib_q)
    libs_sol.append(max_lib)
    # Selection livres
    max_lib.signed = False 
    books_to_scan = max_lib.books_by_worth(
                    time_available=time_available,
                    avoid=avoid)
    max_lib.books_to_scan = books_to_scan
    max_lib.signed = True
    time_available -= max_lib.signup
    avoid |= set(books_to_scan)
    if time_available <= 0:
        break

output(sol_filename, libs_sol)

score = scorer(sys.argv[1],sol_filename)
print("score",score)
