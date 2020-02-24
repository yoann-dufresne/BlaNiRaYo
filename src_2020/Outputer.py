import sys
from src_2020.Library import Library

# Take a list of Librairie object, in the order to use
def output(filename, used_lib):
    to_print = ""
    # number of libraries to sign up
    to_print += str(len(used_lib)) + "\n"
    # ID of the library0 | the number of books to be scanned from library 0
    for i in used_lib:
        to_print += str(i.ide) + " " + str(len(i.books_to_scan)) + "\n"
        # IDs of the books to scan from 0 in the order that they are scanned
        for j in i.books_to_scan:
            if type(j) is int:
                to_print += str(j) + " "
            else:
                to_print += str(j.ide) + " "
        to_print += "\n"
    with open(filename, "w") as output_file:
        output_file.write(to_print)
