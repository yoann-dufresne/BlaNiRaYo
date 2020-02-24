import sys
import src_2020.Parser as Parser

def scorer(input_file, solution_file):
    _, _, nb_days, scores, libs, books = Parser.parse(input_file)
    all_books = set()
    libraries_used = set()
    # assumption: libs are in the order they'll output books
    day = 0
    all_lines = open(solution_file).read().split('\n')
    est_nb_libs = len(all_lines)-1 // 2
    for i, line in enumerate(all_lines):
        if len(line.strip()) == 0: break
        if i == 0:
            nb_libraries = int(line)
            continue
        if i%2 == 1:
            library_id, nb_books = map(int,line.strip().split())

            # safety check
            if library_id in libraries_used:
                print("warning! library %d used twice" % library_id)
            libraries_used.add(library_id)
        else:
            lib_books = list(map(int,line.strip().split()))
            day += libs[library_id].signup
            #print("library",library_id,"nb_books",nb_books)
            #print("books:",lib_books)
            all_books |= set(lib_books)
            remaining_days = nb_days - day
            if len(lib_books) > remaining_days * libs[library_id].ship:
                print("warning! library",library_id,"(number %d/%d in solution)" % (i//2,est_nb_libs),"with capacity",libs[library_id].ship,"outputs more books than it has time for (%d > %d)" % (len(lib_books), remaining_days * libs[library_id].ship))

    print(len(all_books),"books total were selected, ",remaining_days,"unused signup day(s)")
    #print(all_books)

    total_score = 0
    for book in all_books:
        total_score += scores[book]
    print("total score",total_score)
    return total_score


if __name__ == "__main__":
    if len(sys.argv) < 2:
        exit("args: input.txt solution.txt ")
    print(scorer(sys.argv[1],sys.argv[2]))
