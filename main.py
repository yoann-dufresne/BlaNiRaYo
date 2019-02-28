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



def random(photos):
    sol = Solution()
    sol.slides = photos
    return sol


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

<<<<<<< Updated upstream
    (H, V) = split_photos(photos)
    H_slides = list(map(Slide, H))


=======
    sol = random([p for p in photos if p.orientation == "H"])
    sol.save()
>>>>>>> Stashed changes

if __name__ == "__main__":
    main()
