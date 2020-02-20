import sys
import Parser

def scorer(input_file, solution_file):
    _, _, nb_days, scores, libs = Parser.parse(input_file)
    all_books = set()
    # assumption: libs are in the order they'll output books
    day = 0
    for i, line in enumerate(open(solution_file).read().split('\n')):
        print(i,line)
        if len(line.strip()) == 0: break
        if i == 0:
            nb_libraries = int(line)
            continue
        if i%2 == 1:
            print(line)
            library_id, nb_books = map(int,line.strip().split())
        else:
            lib_books = list(map(int,line.strip().split()))
            print("library",library_id,"nb_books",nb_books)
            print("books:",lib_books)
            all_books |= set(lib_books)
            remaining_days = nb_days - day

    print(len(all_books),"books total")
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
