import sys
import Parser

if len(sys.argv) < 2:
    exit("args: solution.txt < input.txt ")

_, _, nb_days, scores, libs = Parser.parse()

solution_file = sys.argv[1]
all_books = set()
for i, line in enumerate(open(solution_file).read().split('\n')):
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

print(len(all_books),"books total")
#print(all_books)

total_score = 0
for book in all_books:
    total_score += scores[book]

print("total score",total_score)
