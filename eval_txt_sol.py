#!/usr/bin/python3

import sys
from Photo import Photo
from Slide import Slide
from Solution import Solution

def split_photos(photos):
    """Return two lists of photos: H, V"""
    H = []
    V = []
    for photo in photos:
        if photo.orientation == "H":
            H.append(photo)
        elif photo.orientation == "V":
            V.append(photo)
    return (H, V)
    

# structure de cette liste:
# (id, orientation, tag0, tag1, tag2, ..)
photos = []
keywords = {}

def compute_score(p1, p2):
    tags1 = set(p1[2])
    tags2 = set(p2[2])
    print(tags1)
    print(tags2)
    return min(len(tags1 & tags2), len(tags1 - tags2), len(tags2 - tags1))


# arguments: [dataset] [solution]

def main():
    global photos
    global keywords
    counter = 0
    for line in open(sys.argv[1]):
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

    solution_file = sys.argv[2]
    sl = open(solution_file).readlines()
    sl = sl[1:]
    sol = Solution()
    for line in sl:
        if len(line.strip().split()) == 1:
            x = int(line.strip())
            sol.slides += [Slide(photos[x])]
        else:
            assert(len(line.strip().split()) == 2)
            x,y = map(int,line.strip().split())
            sol.slides += [Slide(photos[x],photos[y])]
    print("evaluating",len(sol.slides),"slides")
    print("score:",sol.score())


if __name__ == "__main__":
    main()
