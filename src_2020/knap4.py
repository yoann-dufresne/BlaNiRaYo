# this is a strict improvement of knap3 actually

from src_2020.Parser import parse
from src_2020.Outputer import output
from src_2020.Scorer import scorer
from src_2020.Library import mask_books
from src_2020.Dedup import deduplicate_books 
import sys
from collections import defaultdict

if len(sys.argv) < 2:
    exit("args: input_file.txt")

prefix = sys.argv[1][sys.argv[1].index("_")-1]
nb_books, nb_libs, nb_days, scores, libs, books = parse(sys.argv[1])

#libs = deduplicate_books(libs)

L = list(range(len(libs)))
D = list(range(nb_days)) 
B = list(range(nb_books))

do_mip = "--use_saved_mip" not in sys.argv
if do_mip:
    from mip import Model, xsum, maximize, BINARY

    w = [libs[i].signup for i in L]

    book_lib_dict = defaultdict(list)
    book_lib_set = set()
    for lib in libs:
        for book in lib.books:
            book_lib_dict[book.ide] += [lib.ide]
            book_lib_set |= set([(book.ide,lib.ide)])

    print("number of book-lib relationships (out of %d possible): %d" % (nb_books*nb_libs, len(book_lib_set)))

    m = Model('knap solver 4')
    #m.verbose=0

    debug = True
    if debug: print("bl constraints..")

    bl = dict()
    # which book is taken by which lib
    # some sort of bipartite max matching
    # this is what differs from knap3
    for (book, lib) in book_lib_set:
        bl[(book,lib)] = m.add_var(var_type=BINARY)

    # the objective function also differs from knap3
    # no more payoff estimation bs, we optimize directly the real score now!
    m.objective = maximize(xsum(scores[b] * bl[(b,l)] for (b,l) in book_lib_set))

    # book can be assigned to a single library
    for b in B:
        m += xsum(bl[(b,i)] for i in L if (b,i) in book_lib_set) <= 1 

    if debug: print("LxD constraints..")

    l = dict()
    o = dict() # occuped by signup
    for i in L:
        for d in D:
            l[(i,d)] = m.add_var(var_type=BINARY)
            o[(i,d)] = m.add_var(var_type=BINARY)

    # total signup time is respected
    m += xsum(w[i] * l[(i,d)] for i in L for d in D) <= nb_days
    # this is likely a redundant constraint

    # lib can be signed up only once
    for i in L:
        m += xsum(l[(i,d)] for d in D) <= 1

    if debug: print("LxDxsignup constraints..")

    # if a lib is signed up at a certain time, we're occupied during the next days
    for i in L:
        if i % 100 == 0: print(i)
        for d in D:
            for k in range(libs[i].signup):
                if d+k >= nb_days: continue
                m += l[(i,d)] <= o[(i,d+k)]

    # at each day, we can only be occupied by signing up a single library
    for d in D:
        m += xsum(o[(i,d)] for i in L) <= 1

    if debug: print("final bl constraints..")

    # can only take a book if the library has been signed up
    for b,i in book_lib_set:
        m += bl[(b,i)] <= xsum(l[(i,d)] for d in D)
    
    # aaand finally, library can only take a certain number of books until the end
    for i in L:
        m += xsum(bl[(b,i)] for b in B if (b,i) in book_lib_set) <= xsum((nb_days-d-libs[i].signup)*libs[i].ship * l[(i,d)] for d in D)

    # TODO validate it and test it!!

    if debug: print("done with all constraints!")

    #m.optimize(max_seconds=60)
    #m.optimize(max_seconds=100, relax=True)
    #m.optimize(max_solutions=1,relax=True)
    #m.optimize(max_solutions=10,relax=True)
    #m.optimize(max_solutions=100,relax=True)
    m.optimize()

    libs_selected = set([(i,d) for i in L for d in D if l[(i,d)].x >= 0.99])
    books_selected = [(b,i) for (b,i) in book_lib_set if bl[(b,i)].x >= 0.99]

    save=True
    if save:
        f=open(prefix+"_knap4_mip_libs.txt","w")
        f.write(str(libs_selected))
        f.close()
        f=open(prefix+"_knap4_mip_books.txt","w")
        f.write(str(books_selected))
        f.close()

else:
    libs_selected=eval(open(prefix+"_knap4_mip_libs.txt").read().strip())
    books_selected=eval(open(prefix+"_knap4_mip_books.txt").read().strip())

print(len(libs_selected), 'MIP-selected libraries out of ', nb_libs)
total_selected_signup = sum([libs[i].signup for (i,d) in libs_selected])
print(total_selected_signup, 'total signup time out of', nb_days,'days')
print(len(books_selected), 'MIP-selected books out of ', nb_books)
sol_filename = "res_2020/" +  prefix + "_sol.txt" 

libs_sol = []
avoid = set()
for d in D:
    for i in L:
        if (i,d) not in libs_selected: continue
        libs[i].signed = False
        list_lib_books = set([b for (b,j) in books_selected if j == i])
        books_to_scan = [b for b in libs[i].books if b.ide in list_lib_books]
        time_available = nb_days-d-libs[i].signup
        if time_available <= 0 : continue
        books_to_scan = sorted(books_to_scan, key=lambda b:b.score)[::-1][:time_available*libs[i].ship]
        if len(books_to_scan) < time_available*libs[i].ship:
            print("lib",i,"had time to scan",time_available*libs[i].ship-len(books_to_scan),"more books but only did",len(books_to_scan))
        libs[i].books_to_scan = books_to_scan
        libs_sol.append(libs[i])
        avoid |= set(books_to_scan)
        libs[i].signed = True 

print(len(avoid),"books output")
output(sol_filename, libs_sol)

score = scorer(sys.argv[1],sol_filename)
print("score",score)
