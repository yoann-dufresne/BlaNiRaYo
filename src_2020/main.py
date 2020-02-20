import sys
from src_2020.Parser import parse 

if __name__ == "__main__":
    _, _, _, scores, libs = parse()

    print(scores)
