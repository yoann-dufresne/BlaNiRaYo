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
    possibilities = []

    # record all the verticals
    verticals_left = []
    verticals_right = []
    for line in sl:
        if len(line.strip().split()) != 1:
            x,y = map(int,line.strip().split())
            verticals_left += [x]
            verticals_right += [y]
    all_verticals = verticals_left + verticals_right

    for shift in range(len(verticals_right)):
        # construct a solution with that shift
        sol = Solution()
        for i, line in enumerate(sl):
            if len(line.strip().split()) == 1:
                x = int(line.strip())
                sol.slides += [Slide(photos[x])]
            else: # vertical
                assert(len(line.strip().split()) == 2)
                x,y = map(int,line.strip().split())
                y = verticals_right[(i+shift) % len(verticals_right)] # substitute with shifted
                #x = all_verticals[(i+shift) % len(all_verticals)]
                #y = all_verticals[(i++len(verticals_left)+shift) % len(all_verticals)]
                sol.slides += [Slide(photos[x],photos[y])]
     
        print("evaluating",len(sol.slides),"slides")
        score = sol.score()
        print("score:",score)
        possibilities += [(score,sol)]

    print("best score",max(possibilities)[0])

if __name__ == "__main__":
    main()
