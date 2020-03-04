# this is knap5 with some preprocessing and all libs are unordered
# was doing some tests to get scores for instance d

from src_2020.Parser import parse
from src_2020.Outputer import output
from src_2020.Scorer import scorer
from src_2020.Library import mask_books
from src_2020.Dedup import deduplicate_books 
from src_2020.IntersectLibs import intersect_libs 
import sys
from collections import defaultdict, Counter

if len(sys.argv) < 2:
    exit("args: input_file.txt")

prefix = sys.argv[1][sys.argv[1].index("_")-1]
nb_books, nb_libs, nb_days, scores, libs, books = parse(sys.argv[1])

# parameters for d instance only (not really optimizing the other instances at the moment)
libsize_cutoff = 5
autoselect_libsize = -1

if libsize_cutoff != 0:
    remember_lib_ide = dict()
    intersections = intersect_libs(libs)
    
    big_libs = set([lib.ide for lib in libs if len(lib.books) >= 10])
    books_in_big_libs = set([b for i in big_libs for b in libs[i].books])

    # now keep only the small libs that don't intersect too much with the big ones
    list_inter_with_bigs = [] 
    def big_or_small_with_small_intersection(i):
        global list_inter_with_bigs
        if len(libs[i].books) >= 7: return True
        inter_with_bigs = set(libs[i].books) & books_in_big_libs
        list_inter_with_bigs += [len(inter_with_bigs)]
        return len(inter_with_bigs) <= 2

    #libs = [lib for lib in libs if len(lib.books) >= libsize_cutoff]
    libs = [lib for lib in libs if big_or_small_with_small_intersection(lib.ide)]

    print(Counter(list_inter_with_bigs))

    for i,lib in enumerate(libs):
        remember_lib_ide[i] = lib.ide
        lib.ide = i
    nb_libs = len(libs)

    print("number of libs now:",nb_libs)
    # gurobi seems to struggle with 25K libs but not with 22K libs


#libs = deduplicate_books(libs)

L = list(range(len(libs)))
D = list(range(nb_days)) 
B = list(range(nb_books))


do_mip = "--use_saved_mip" not in sys.argv
if do_mip:
    from mip import Model, xsum, maximize, BINARY, INTEGER

    w = [libs[i].signup for i in L]

    book_lib_dict = defaultdict(list)
    book_lib_set = set()
    for lib in libs:
        for book in lib.books:
            book_lib_dict[book.ide] += [lib.ide]
            book_lib_set |= set([(book.ide,lib.ide)])

    print("number of book-lib relationships (out of %d possible): %d" % (nb_books*nb_libs, len(book_lib_set)))

    m = Model('knap solver 5')
    #m.verbose=0

    bl = dict()
    # which book is taken by which lib
    for (book, lib) in book_lib_set:
        bl[(book,lib)] = m.add_var(var_type=BINARY)

    m.objective = maximize(xsum(scores[b] * bl[(b,l)] for (b,l) in book_lib_set))

    debug = True
    if debug: print("bl constraints..")

    # book can be assigned to a single library
    for b in B:
        m += xsum(bl[(b,i)] for i in book_lib_dict[b]) <= 1 

    if debug: print("LxD constraints..")

    # the unordered libraries
    ul = [m.add_var(var_type=BINARY) for i in L]

    # assign the number of unordered days
    m += xsum(w[i] * ul[i] for i in L) <= nb_days

    # force some libs to be used
    if autoselect_libsize > 0:
        for lib in libs:
            if len(lib.books) >= autoselect_libsize:
                m += ul[lib.ide] == 1
    
    # lib can be signed up only once
    for i in L:
        m += ul[i] <= 1

    if debug: print("final bl constraints 1..")

    # can only take a book if the library has been signed up
    for b,i in book_lib_set:
        m += bl[(b,i)] <= ul[i]
    
    if debug: print("final bl constraints 2..")
   
    # aaand finally, library can only take a certain number of books until the end
    for i in L:
        m += xsum(bl[(b.ide,i)] for b in libs[i].books) <= len(libs[i].books)*ul[i] # here we ignore edge effects of the last ul library..

    if debug: print("done with all constraints!")

    #m.optimize(max_seconds=60)
    #m.optimize(max_solutions=1,relax=True)
    #m.optimize(max_solutions=10,relax=True)
    #m.optimize(max_solutions=100,relax=True)
    #m.optimize(max_seconds=200)
    #m.optimize()
    m.optimize(max_solutions=5)

    ulibs_selected = set([i for i in L if ul[i].x >= 0.99])
    books_selected = [(b,i) for (b,i) in book_lib_set if bl[(b,i)].x >= 0.99]

    save=True
    if save:
        f=open(prefix+"_knap6_mip_ulibs.txt","w")
        f.write(str(ulibs_selected))
        f.close()
        f=open(prefix+"_knap6_mip_books.txt","w")
        f.write(str(books_selected))
        f.close()

else:
    ulibs_selected=eval(open(prefix+"_knap6_mip_ulibs.txt").read().strip())
    books_selected=eval(open(prefix+"_knap6_mip_books.txt").read().strip())

print(len(ulibs_selected), 'MIP-selected unordered libraries out of ', nb_libs)
total_selected_signup = sum([libs[i].signup for i in ulibs_selected])
print(total_selected_signup, 'total signup time out of', nb_days,'days')
print(len(books_selected), 'MIP-selected books out of ', nb_books)
sol_filename = "res_2020/" +  prefix + "_sol.txt" 

# retrieve the solution lib order
selected_libs = list(ulibs_selected)

libs_sol = []
avoid = set()
day = 0

scanned_books_lib = defaultdict(list)
for b,i in books_selected:
    scanned_books_lib[b] += [i]

for i in selected_libs:
        lib_status = "unordered"
        libs[i].signed = False
        list_lib_books = set([b for (b,j) in books_selected if j == i])
        books_to_scan = [b for b in libs[i].books if b.ide in list_lib_books]
        day += libs[i].signup
        time_available = nb_days-day
        if time_available <= 0 : continue
        if len(books_to_scan) > time_available*libs[i].ship:
            print(lib_status,"lib",i,"has assigned more books %d to scan than available time (%d), cutting them" % (len(books_to_scan), time_available*libs[i].ship))
            books_to_scan = sorted(books_to_scan, key=lambda b:b.score)[::-1][:time_available*libs[i].ship] 
        unscanned_books = set(libs[i].books) - set(books_to_scan)
        # determine cases where unselected books are actually scanned by another lib
        for b in list(unscanned_books):
            if b.ide in scanned_books_lib:
                #print("book",b.ide,"unscanned by lib",i,"is actually scanned by lib",scanned_books_lib[b.ide])
                unscanned_books -= set([b])
        nb_unscanned_books = len(unscanned_books)
        time_to_scan_books = len(books_to_scan) / libs[i].ship
        nb_unscanned_books_in_time_available = min(nb_unscanned_books, time_available*libs[i].ship)
        if  nb_unscanned_books > 0 and time_available > time_to_scan_books:
            print(lib_status,"lib",i,"timespan",day-libs[i].signup,day,"had time to scan",nb_unscanned_books_in_time_available,"more books but only did",len(books_to_scan))
            rescue_pile = []
            for b in unscanned_books:
                rescue_pile += [b]
            rescue_pile = rescue_pile[:nb_unscanned_books_in_time_available]
            books_to_scan += rescue_pile
            print("rescued",len(rescue_pile),"books (that should not have happened if MIP was correct)")

        libs[i].books_to_scan = books_to_scan
        libs_sol.append(libs[i])
        avoid |= set(books_to_scan)
        libs[i].signed = True 

if libsize_cutoff != 0:
        for lib in libs_sol:
                lib.ide = remember_lib_ide[lib.ide]

print(len(avoid),"books output")
output(sol_filename, libs_sol)

score = scorer(sys.argv[1],sol_filename)
print("score",score)
