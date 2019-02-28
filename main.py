#!/usr/bin/python3

import sys


# structure de cette liste:
# (id, orientation, tag0, tag1, tag2, ..)
photos = []
keywords = {}

def main():
    global photos
    global keywords
    counter = 0
    for line in sys.stdin:
        if len(line.split()) == 1:
            nb_photos = int(line.strip())
        else:
            photos += [(counter, *line.strip().split()[0], line.strip().split()[2:])]
            for kw in photos[-1][2]:
                if not kw in keywords:
                    keywords[kw] = []
                keywords[kw].append(photos[-1])
            counter += 1
    assert(counter == len(photos) and counter == nb_photos)

    print(len(keywords), "keywords")

    print(len(photos),"photos parsed")

if __name__ == "__main__":
    main()
