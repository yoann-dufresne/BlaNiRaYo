import sys
from src_2020.Parser import parse

# from mip import Model, xsum, maximize, BINARY, INTEGER


def mip_select_libs(books, libs, max_time):
    # --- Pre-process ---

    lib_per_books = {b.ide:[] for b in books}
    for lib in libs:
        for b in lib.books():
            lib_per_books[b.ide].append(lib.ide)


    # --- Model ---

    m = Model('knap lib select for small amount of book per lib')
    m.verbose=1
    m.threads = 6

    # --- Variables ---
    
    lib_selection = [m.add_var(var_type=BINARY) for _ in libs]
    book_selection = [m.add_var(var_type=INTEGER) for _ in books]
    book_presence = [m.add_var(var_type=BINARY) for _ in books]


    # --- Constraints ---

    # books scanned
    print("Book count constraints")
    for i in range(len(books)):
        if (i % 100) == 99:
            print(f"\r{i+1}/{len(books)}", end="")
        m += book_selection[i] == xsum(lib_selection[x] for x in lib_per_books[i])
        m += book_presence[i] <= book_selection[i]
    print()
    print("Book presence constraints")
    for book_idx in lib_per_books:
        if (book_idx % 100) == 99:
            print(f"\r{book_idx+1}/{len(books)}", end="")
        for lib_idx in lib_per_books[book_idx]:
            m += book_presence[book_idx] >= lib_selection[lib_idx]
    print()
    # time limit
    m += xsum(libs[idx].signup * l for idx, l in enumerate(lib_selection)) <= max_time-1


    # --- Optimization ---

    m.objective = maximize(xsum((presence*books[book_idx].score) for book_idx, presence in enumerate(book_presence)))

    print("Start optimization")
    status = m.optimize(max_seconds=100, max_solutions=10,relax=True)
    print(status)

    return [libs[idx] for idx, selected in enumerate(lib_selection) if selected.x >= 0.99]


from itertools import combinations, permutations
from src_2020.Solution import Solution
import random

def compute_sol(libs, nb_days):
    total_register_time = sum(lib.signup for lib in libs)
    opti = None
    best_score = 0

    lib_set = set(libs)
    combs = list(combinations(libs, 6))
    random.shuffle(combs)

    for comb in combs:
        # initial solution
        # Add the permutations
        for perm in permutations(comb, len(comb)):
            sol = Solution(lib_set - set(comb))
            sol.libs.extend(list(perm))
            # remaining_time = nb_days - total_register_time + sum(lib.signup for lib in comb)
            sol.set_all_books(nb_days)
            if sol.get_score() > best_score:
                yield sol
                best_score = sol.get_score()
        

from Outputer import output

if __name__ == "__main__":
    nb_days, books, libs = parse()

    # Compute selection
    # selected = mip_select_libs(books, libs, nb_days)
    # print([l.ide for l in selected])

    # Reload selection from previous computation
    selected = [147, 204, 209, 210, 312, 369, 422, 454, 595, 618, 622, 672, 694, 719, 774, 828, 901]
    selected = [libs[s] for s in selected]

    # Stats
    # for lib in selected:
    #     print(lib.signup, lib.days_to_complete(), lib.days_to_complete()-lib.signup)
    # print(sum(sorted([lib.signup for lib in selected])[:6]))

    for sol in compute_sol(selected, nb_days):
        print(sol.get_score())
        output(f"res_2020/e_{sol.get_score()}.txt", sol.libs)
