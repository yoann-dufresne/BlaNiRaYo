#!/usr/bin/python3

import sys
from random import shuffle
from Photo import Photo
from Slide import Slide
from Solution import Solution
from HillClimbing import HillClimbing as HC

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

def sol_blaise_1(photos):
    (H, V) = split_photos(photos)
    H_slides = list(map(Slide, H))
    nb_V = len(V)
    V_slides = [Slide(p1, p2) for (p1, p2) in zip(V[:nb_V//2], V[nb_V//2:])]
    sol = Solution()
    sol.slides = V_slides + H_slides
    return sol

def sol_blaise_2(photos):
    (H, V) = split_photos(photos)
    max_score = 0
    best_sol = None
    for _ in range(100):
        shuffle(H)
        shuffle(V)
        H_slides = list(map(Slide, H))
        nb_V = len(V)
        V_slides = [Slide(p1, p2) for (p1, p2) in zip(V[:nb_V//2], V[nb_V//2:])]
        sol = Solution()
        sol.slides = V_slides + H_slides
        if best_sol is None:
            best_sol = sol
            max_score = sol.score()
        else:
            if sol.score() > max_score:
                best_sol = sol
                max_score = sol.score()
    return best_sol


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

    #sol = random([p for p in photos if p.orientation == "H"])
    #sol.save()
    (H, V) = split_photos(photos)
    H_slides = list(map(Slide, H))
    nb_V = len(V)
    V_slides = [Slide(p1, p2) for (p1, p2) in zip(V[:nb_V//2], V[nb_V//2:])]
    sol = Solution()
    if len(sys.argv) > 2:
        sol = Solution(photos=photos, file=sys.argv[2])
    if len(sol.slides) == 0:
        sol.slides = V_slides + H_slides

    # sol = sol_blaise_2(photos)
    # sol.save()
    #for _ in range(100):
    #    shuffle(sol.slides)
    #    sol.save()

    hc = HC(sol)
    hc.climb()


if __name__ == "__main__":
    main()
