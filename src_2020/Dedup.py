def deduplicate_books(libs,duplication_threshold=1): 
    #,nb_books_threshold=50): # not ready to do that kind of filtering, see below
    import heapq
    from copy import deepcopy
    from collections import Counter
    booksc = Counter()
    dedup_libs = deepcopy(libs)
    for lib in libs:
        for book in lib.books:
            booksc[book.ide] += 1
    print("average frequency of a book",sum([booksc[b] for b in booksc]) / len(booksc))
    from statistics import mean, stdev, median
    books_in_lib = [len(lib.books) for lib in libs]
    print("books per lib before deduplication, mean %.2f / median %d / stdev %.2f / max %d / min %d" \
        %(mean(books_in_lib),median(books_in_lib),stdev(books_in_lib),max(books_in_lib),min(books_in_lib)))

    libq = []
    # use a pq to control how imbalance when removing books from libraries,
    # possible strategies:
    # - making them as evenly containing books as possible
    # - force some libs to have as many books as poss (and schedule them at the beginning)
    #selection_function = lambda lib_i: len(dedup_libs[lib_i].books)
    #selection_function = lambda lib_i: -len(dedup_libs[lib_i].books)
    #selection_function = lambda lib_i: lib_i
    #selection_function = lambda lib_i: len(dedup_libs[lib_i].books)/(lib_i+1)
    #selection_function = lambda lib_i: -sum([book.score for book in dedup_libs[lib_i].books])
    #selection_function = lambda lib_i: -len(dedup_libs[lib_i].books) / dedup_libs[lib_i].ship
    #selection_function = lambda lib_i: -dedup_libs[lib_i].urgency # best setting for knap3/e dataset. but huh, minus sign doesn't change anything?
    selection_function = lambda lib_i: -dedup_libs[lib_i].urginvworth
    #selection_function = lambda lib_i: dedup_libs[lib_i].libworth
    #selection_function = lambda lib_i: -dedup_libs[lib_i].testing
    for lib_i,lib in enumerate(dedup_libs):
        heapq.heappush(libq, (selection_function(lib_i), lib_i))
    while len(booksc) > 0:
        _, lib_i = heapq.heappop(libq)
        deleted_a_book = False
        for book in dedup_libs[lib_i].books:
            if book.ide in booksc:
                if booksc[book.ide] > duplication_threshold:
                    dedup_libs[lib_i].books.remove(book)
                    booksc[book.ide] -= 1
                if booksc[book.ide] <= duplication_threshold:
                    del booksc[book.ide]
                deleted_a_book = True
                break
        if deleted_a_book: # if not: nothing to do anymore for this lib
            heapq.heappush(libq, (selection_function(lib_i), lib_i))
    
    # to speed up later mip: don't consider small libs
    # requires to make libs a dict instead of a list 
    # else we lose identifiers and correspondence of IDs with original instance
    # but..
    """
    # this code isn't ready for primetime, because we often use "lib.books for lib in libs" but that wouldn't work if libs is a dictionary
    dedup_libs = dict([(lib.ide,lib) for lib in dedup_libs if len(lib.books) > nb_books_threshold])
    if len(dedup_libs) != len(libs):
        print("removed",len(libs)-len(dedup_libs),"libraries, now at",len(dedup_libs))
    """

    books_in_lib = [len(lib.books) for lib in dedup_libs]
    print("books per lib after deduplication, mean %.2f / median %d / stdev %.2f / max %d / min %d"% \
        (mean(books_in_lib),median(books_in_lib),stdev(books_in_lib),max(books_in_lib),min(books_in_lib)))

    return dedup_libs

# not ready for primetime
def smooth_books(libs,duplication_threshold=1):
    booksc = Counter()
    smooth_libs = deepcopy(libs)
    for lib in libs:
        for book in lib.books:
            booksc[book.ide] += 1
    print("average frequency of a book",sum([booksc[b] for b in books]) / len(books)) 
    categories = dict()
    for lib in smooth_libs:
        #lib.time_needed = len(lib.books) / lib.ship
        #categories[lib.time_needed] = lib.ide
        pass
    print(categories)
    libq = []
    # use a pq to control how imbalance when removing books from libraries, 
    # possible strategies:
    # - making them as evenly containing books as possible
    # - force some libs to have as many books as poss (and schedule them at the beginning)
    for lib_i,lib in enumerate(dedup_libs):
        heapq.heappush(libq, (len(lib.books), lib_i))
    while len(booksc) > 0:
        _, lib_i = heapq.heappop(libq)
        deleted_a_book = False
        for book in dedup_libs[lib_i].books:
            if book.ide in booksc:
                if booksc[book.ide] > duplication_threshold:
                    dedup_libs[lib_i].books.remove(book)
                    booksc[book.ide] -= 1
                if booksc[book.ide] <= duplication_threshold:
                    del booksc[book.ide]
                deleted_a_book = True
                break
        if deleted_a_book: # if not: nothing to do anymore for this lib
            heapq.heappush(libq, (len(dedup_libs[lib_i].books), lib_i))
    return dedup_libs


