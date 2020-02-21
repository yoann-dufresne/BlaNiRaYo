import sys
from src_2020.Parser import parse

if __name__ == "__main__":
    nb_books, nb_libs, nb_days, scores, libs, books = parse()

    print(scores)
