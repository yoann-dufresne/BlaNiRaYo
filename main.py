#!/usr/bin/python3

import sys


# structure de cette liste:
# (id, orientation, tag0, tag1, tag2, ..)
photos = []

def main():
    global photos
    counter = 0
    for line in sys.stdin:
        if len(line.split()) == 1:
            nb_photos = int(line.strip())
        else:
            photos += [(counter, *line.strip().split()[0], *line.strip().split()[2:])]
            counter += 1
    assert(counter == len(photos) and counter == nb_photos)

    print(len(photos),"photos parsed")
    print(photos)

if __name__ == "__main__":
    main()
