# returns a dictionary saying how big is the intersection of libs (i,j)
# if the key isn't in the dictionary, the intersection is zero
# can't do it naively for dataset d because 30000x30000 is too big
def intersect_libs(libs): 
    from collections import defaultdict
    print("computing intersections..")
    book_lib_dict = defaultdict(list)
    book_lib_set = set()
    for lib in libs:
        for book in lib.books:
            book_lib_dict[book.ide] += [lib.ide]

    res = dict()
    for lib in libs:
        for book in lib.books:
            for lib2 in book_lib_dict[book.ide]:
                if lib2 == lib.ide: continue
                res[(lib.ide,lib2)] = len(set(lib.books) & set(libs[lib2].books))

    print(len(res),"non-zero intersections computed.")
    return res
