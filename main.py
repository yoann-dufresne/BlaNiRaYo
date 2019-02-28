#!/usr/bin/python3

import sys
from Photo import Photo

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
            photos += [Photo(counter, *line.strip().split()[0], line.strip().split()[2:])]
            for kw in photos[-1].keywords:
                if not kw in keywords:
                    keywords[kw] = []
                keywords[kw].append(photos[-1])
            counter += 1
    assert(counter == len(photos) and counter == nb_photos)

    print(len(keywords), "keywords")

    print(len(photos),"photos parsed")
    #print(photos)

if __name__ == "__main__":
    main()
