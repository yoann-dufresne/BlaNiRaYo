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
    return min(len(tags1 & tags2), len(tags1 - tags2), len(tags2 - tags1))

def compute_score_tags(tags1, tags2):
    return min(len(tags1 & tags2), len(tags1 - tags2), len(tags2 - tags1))


from collections import defaultdict
index = defaultdict(list)

import os
import pickle

prefix = "e"

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


if not os.path.exists(prefix + "_index.pickle"):
    for (i,p) in enumerate(photos):
        print("indexing",i)
        tags = p.keywords
        for tag1 in tags:
            for tag2 in tags:
                if tag1 < tag2:
                    index[(tag1,tag2)] += [i]
    pickle_file = open(prefix + "_index.pickle","wb")
    pickle.dump(index,pickle_file)
    pickle_file.close()

    print(prefix + " index computed",len(index))

pickle_file = open(prefix + "_index.pickle","rb")
index = pickle.load(pickle_file)
pickle_file.close()
print(prefix + " index loaded",len(index))


def close_sets(tags):
    candidates = []
    for tag1 in tags:
        for tag2 in tags:
            if tag1 < tag2:
                if (tag1, tag2) in index:
                    candidates += index[(tag1,tag2)]
    return set(candidates)


remaining = set(list(range(len(photos))))

def find_best_pair(current):
    global used, remaining
    tags_current = set(current.keywords)
    candidates = []
    explored = 0
    for j in remaining:
        tags_candidate = set(photos[j].keywords)
        score = compute_score_tags(tags_current,tags_candidate)
        candidates += [(score,j)]
        if explored > 1000: break # heuristic
        explored += 1
    if len(candidates) == 0:
        candidates = [(0,list(remaining)[0])] # hack
    selected = max(candidates)[1]
    remaining -= set([selected])
    print("max",max(candidates))
    return selected

def find_next_start(tags_list):
    global used, remaining
    candidates = []
    explored = 0
    for j in remaining:
        tags_candidate = set(photos[j].keywords)
        score = compute_score_tags(tags_list,tags_candidate)
        candidates += [(score,j)]
        if explored > 1000: break # heuristic
        explored += 1
    if len(candidates) == 0:
        candidates = [(0,list(remaining)[0])] # hack
    selected = max(candidates)[1]
    remaining -= set([selected])
    print("max",max(candidates))
    return selected


sol = Solution()
sol.slides = []
current = photos[0] # start from photo 0
while True:
    if len(remaining) < 3: # hack
        break
    # find best photo to pair
    paired_with = find_best_pair(current)
    sol.slides += [Slide(current,photos[paired_with])] 
    print(current.id,paired_with)
    nxt = find_next_start(set(current.keywords) | set(photos[paired_with].keywords))
    current = photos[nxt]
    remaining -= set([current.id])

sol.save()


