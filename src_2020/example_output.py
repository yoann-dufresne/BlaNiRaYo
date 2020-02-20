import sys
from src_2020.Library import Library, Book
import Outputer

if __name__ == "__main__":


    a_lib = Library(0, 1, 2)
    a_book = Book(3, 4)
    b_book = Book(5, 6)
    a_lib.add_books(a_book)
    a_lib.add_books(b_book)

    b_lib = Library(7, 8, 9)
    c_book = Book(10, 11)
    d_book = Book(12, 13)
    b_lib.add_books(c_book)
    b_lib.add_books(d_book)

    filename = "jeux_A.txt"
    Outputer.output(filename, [b_lib, a_lib])
