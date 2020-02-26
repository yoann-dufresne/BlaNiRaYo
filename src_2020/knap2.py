from src_2020.Parser import parse
from src_2020.Outputer import output
from src_2020.Scorer import scorer
from src_2020.Library import mask_books
from src_2020.Dedup import deduplicate_books 
import sys

if len(sys.argv) < 2:
    exit("args: input_file.txt")

prefix = sys.argv[1][sys.argv[1].index("_")-1]
nb_books, nb_libs, nb_days, scores, libs, books = parse(sys.argv[1])

#libs = deduplicate_books(libs)

do_mip = "--use_saved_mip" not in sys.argv
if do_mip:
    from mip import Model, xsum, maximize, BINARY

    L = list(range(len(libs)))
    B = list(range(nb_books))
    w = [libs[i].signup for i in L]

    print("subscription times", w[:10])

    m = Model('knap solver 2')
    m.verbose=0

    l = [m.add_var(var_type=BINARY) for i in L]
    b = [m.add_var(var_type=BINARY) for i in B]

    # this is to add some weight to the total signup time in the MIP
    f_factor = 0
    if prefix == "f":
        f_factor = 4000 # the small tweak that gives 5.204 in instance f (with urgency greedy)
    elif prefix == "c":
        f_factor = 0.5  # the small tweak that gives 5.690 in instance c
    #f_factor = float(sys.argv[2]) #hack, use it like this: for i in `seq 1 2 40` ;do python knap2.py ../data/f_libraries_of_the_world.txt $i; done
    if f_factor != 0:
        print("f_factor",f_factor)

    #m.objective = maximize(xsum(p[i] * x[i] for i in I))
    #m.objective = maximize(xsum(scores[i] * b[i] for i in B))
    m.objective = maximize(xsum(scores[i] * b[i] for i in B) + f_factor*xsum(-libs[i].signup * l[i] for i in L)) 

    adjust_nb_days = 0
    if prefix == "f":
        adjust_nb_days = 30 # make instance f think it has slightly less days
    #adjust_nb_days = int(sys.argv[2]) #hack, use it like this: for i in `seq 1 2 40` ;do python knap2.py ../data/f_libraries_of_the_world.txt $i ; done
    if adjust_nb_days != 0:
        print("adjusted nb_days:",-adjust_nb_days)

    m += xsum(w[i] * l[i] for i in L) <= nb_days - adjust_nb_days

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

print(len(libs_selected), 'MIP-selected libraries out of ', nb_libs)
total_selected_signup = sum([libs[i].signup for i in libs_selected])
print(total_selected_signup, 'total signup time out of', nb_days,'days')
print(len(books_selected), 'MIP-selected books out of ', nb_books)
sol_filename = "res_2020/" +  prefix + "_sol.txt" 

# is there still time to fit a small library? try it
maybe_to_add = []
if adjust_nb_days != 0:
    grignotage = []
    all_books = set([b for lib in libs for b in lib.books])
    avoid = [b for b in all_books if b.ide in books_selected] 
    for j in range(len(libs)):
        if j in libs_selected: continue
        if libs[j].signup + 1 <= nb_days - total_selected_signup:
            libs[j].signed = False
            gain = sum([book.score for book in libs[j].books_by_worth(time_available=nb_days - total_selected_signup, avoid=avoid)])
            print("there's still some time to select lib %d (signup=%d), hoping to gain %d" % (libs[j].ide, libs[j].signup, gain))
            grignotage += [(gain,j)]
    if len(grignotage) > 0:
        maybe_to_add += [libs[max(grignotage)[1]]]

libs = [libs[i] for i in libs_selected]

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
        heapq.heappush(lib_q, (-lib.urgency, lib)) # best strat for dataset f
        #heapq.heappush(lib_q, (-lib.urginvworth, lib))
        #heapq.heappush(lib_q, (-lib.signup, lib)) 
        #heapq.heappush(lib_q, (lib.ship, lib))
iteration = 0
update_lib_queue()
while len(lib_q) > 0 or len(maybe_to_add) > 0:
    if nb_libs < 10000 or iteration % 50 == 1:
        update_lib_queue()
    iteration += 1
    # add that one last lib
    if len(lib_q) == 0 and len(maybe_to_add) > 0:
        max_lib = maybe_to_add[0]
        maybe_to_add = maybe_to_add[1:]
    else:
        value, max_lib = heapq.heappop(lib_q)
    # Selection livres
    max_lib.signed = False 
    books_to_scan = max_lib.books_by_worth(
                    time_available=time_available,
                    avoid=avoid)
    nb_unselected_books = 0
    for book in books_to_scan:
        if book.ide not in books_selected:
            nb_unselected_books += 1
    if nb_unselected_books > 0:
        print("warning! lib %d picking up book %d not selectde by MIP" % (max_lib.ide,nb_unselected_books))
    max_lib.books_to_scan = books_to_scan
    max_lib.signed = True
    libs_sol.append(max_lib)
    time_available -= max_lib.signup
    avoid |= set(books_to_scan)
    if time_available <= 0:
        break

output(sol_filename, libs_sol)

scorer(sys.argv[1],sol_filename)
