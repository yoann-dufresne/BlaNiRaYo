
#!/usr/bin/python3
from Photo import Photo
from Slide import Slide
from Solution import Solution

import math
import random
from itertools import combinations
import pickle
import os
from collections import defaultdict
import sys
import networkx as nx

#CHANGEME
score_threshold = 6 #minimum interest
prefix = sys.argv[1].split("_")[0]

# structure de cette liste:
# (id, orientation, tag0, tag1, tag2, ..)
photos = []
keywords = {}

# load data file
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
 
print(len(keywords), "keywords")

print(len(photos),"photos parsed")
#print(photos)

# switch tags to something less expensive
tags_set = set()
for photo in photos:
    tags_set |= set(photo.keywords)
tags_list = list(tags_set)
tags_dict = {}
for i,tag in enumerate(tags_list):
    tags_dict[tag] = i

for i, photo in enumerate(photos):
    new_keywords = []
    for tag in photo.keywords:
        new_keywords += [tags_dict[tag]]
    photos[i].keywords = set(new_keywords)


(H, V) = split_photos(photos)
H_slides = list(map(Slide, H))
nb_V = len(V)
V_slides = [Slide(p1, p2) for (p1, p2) in zip(V[:nb_V//2], V[nb_V//2:])]

#slides = V_slides + H_slides
#print(len(slides),"slides created from original input")
print(len(H),"horizontal and",len(V),"vertical photos")



# from this point: the optimizer function
# scroll to the end to see how it is used

#print(photos)

def compute_score(s1, s2):
    tags1 = s1.keywords
    tags2 = s2.keywords
    return min(len(tags1 & tags2), len(tags1 - tags2), len(tags2 - tags1))

def optimize(slides):
    valid_edges = defaultdict(list)
    distances = {}
    index = defaultdict(list)
    index3 = defaultdict(list)
    index4 = defaultdict(list)

    always_recreate_indices = True 
    #always_recreate_indices = False 

    if always_recreate_indices or not os.path.exists(prefix + "_index.pickle"):
        for (i,p) in enumerate(slides):
            tags = p.keywords
            for tag1,tag2,tag3,tag4 in combinations(sorted(tags),4):
                index4[(tag1,tag2,tag3,tag4)] += [i]
            for tag1,tag2,tag3 in combinations(sorted(tags),3):
                index3[(tag1,tag2,tag3)] += [i]
            for tag1,tag2 in combinations(sorted(tags),2):
                index[(tag1,tag2)] += [i]
        pickle_file = open(prefix + "_index.pickle","wb")
        pickle.dump((index,index3, index4),pickle_file)
        pickle_file.close()

        print(prefix + " index computed")
    
    always_recreate_distances = True 
    #always_recreate_distances = False 

    if always_recreate_distances or not os.path.exists(prefix + "_distances.pickle"):
        pickle_file = open(prefix + "_index.pickle","rb")
        index, index3, index4 = pickle.load(pickle_file)
        pickle_file.close()
        print(prefix + " index loaded")


        def close_sets(tags):
            candidates = []
            for tag1 in tags:
                for tag2 in tags:
                    if tag1 < tag2:
                        if (tag1, tag2) in index:
                            candidates += index[(tag1,tag2)]
            return set(candidates)

        def close_sets_3(tags):
            candidates = []
            for tag1,tag2,tag3 in combinations(sorted(tags),3):
                if (tag1, tag2, tag3) in index3:
                    candidates += index3[(tag1,tag2, tag3)]
            return set(candidates)

        def close_sets_4(tags):
            candidates = []
            for tag1,tag2,tag3,tag4 in combinations(sorted(tags),4):
                if (tag1, tag2, tag3, tag4) in index4:
                    candidates += index4[(tag1,tag2, tag3, tag4)]
            return set(candidates)


        nb_edges = 0
        for i,p1 in enumerate(slides):
            if i % 500 == 0: print(i,"edges so far:",nb_edges)
            tags = p1.keywords
            #print(len(close_sets_3(tags)),"indsteadof ",len(slides))
            for j in close_sets_4(tags):
                if j > i: continue # will be symmetrical
                p2 = slides[j]
                score = compute_score(p1,p2)
                if score > score_threshold:
                    distances[(i,j)] = score
                    nb_edges += 1

        pickle_file = open(prefix + "_distances.pickle","wb")
        pickle.dump(distances,pickle_file)
        pickle_file.close()
        print(prefix + " distances computed,",nb_edges,"edges",len(distances),"distances")

    pickle_file = open(prefix + "_distances.pickle","rb")
    distances = pickle.load(pickle_file)
    pickle_file.close()
    print(prefix + " distances loaded",len(distances))

    n = len(slides)

    import gurobipy 

    m = gurobipy.Model()

    def distance_func(i,j):
        if j > i:
            i,j = j,i
        if (i,j) in distances:
            return distances[(i,j)]
        return 0

    # Create variables

    vars = {}
    for i,j in distances:
        valid_edges[i] += [j]
        vars[i,j] = m.addVar(obj=distance_func(i, j), vtype=gurobipy.GRB.BINARY,name='e'+str(i)+'_'+str(j))
        vars[j,i] = vars[i,j]
    m.update()

    #print(distances)
    # dunno
    for i in range(n):
        vars[i,i] = m.addVar(obj=distance_func(i, i), vtype=gurobipy.GRB.BINARY,name='e'+str(i)+'_'+str(i))

    print("variables created")


    # Add degree-2 constraint, and forbid loops

    for i in range(n):
	    m.addConstr(gurobipy.quicksum(vars[i,j] for j in valid_edges[i] ) <= 2)
	    vars[i,i].ub = 0

    m.update()

    print("constraints made")

    # Optimize model

    m._vars = vars
    m.params.LazyConstraints = 1
    #m.optimize(subtourelim) # see tsp.py from Gurobi constraints for a possible optimization

    m.modelSense = gurobipy.GRB.MAXIMIZE
    m.optimize()

    solution = m.getAttr('x', vars)
    #print("solution",solution)
    selected = [(i,j) for (i,j) in distances if solution[i,j] > 0.5]
    #print("selected",selected)

    # walk the solution
    g = nx.Graph()

    for e in selected:
        g.add_edge(*e)

    print("number connected components:", nx.number_connected_components(g))

    nb_nodes = len(g.nodes())

    solution = []
    for i,connected_component_2 in enumerate(nx.connected_component_subgraphs(g)):
        connected_component = nx.Graph(connected_component_2)
        if i == 0:
            nx.write_gexf(connected_component,prefix+"_component0.gexf")
        done = False
        while not done :
            extremity_candidates = [x for x in connected_component.nodes() if connected_component.degree(x) == 1]
            if len(extremity_candidates) == 0:
                print("it's a cycle")
                if len(connected_component.nodes()) == 0:
                    print("no node?")
                    done = True
                    break
                extremity = list(connected_component.nodes())[0]
            else:
                extremity = extremity_candidates[0]
            print("connected component index",i,"node number",extremity,len(connected_component),"nodes remaining")
            nxt = extremity
            solution += [nxt]
            while True:
                if len(connected_component.nodes()) == 0:
                    done = True
                    break
                nxt_set = set(connected_component.neighbors(nxt))
                connected_component.remove_node(nxt)
                if len(nxt_set) == 0:
                    #start again with a new node
                    break
                #print("deleting",nxt, "next one is",list(nxt_set)[0])
                nxt = list(nxt_set)[0]
                #print(i,nxt)
                solution += [nxt]
    return solution

print("optimizing",len(V),"verticals-only first")

solution = optimize(V)

sol1, sol2 = solution[:len(solution)//2], solution[len(solution)//2:]

grouped_V = []
for (photo1, photo2) in zip(sol1,sol2):
    grouped_V += [Slide(V[photo1],V[photo2])]

slides2 = grouped_V + H_slides
solution_4real = optimize(slides2)

f = open("sol_" + prefix + ".txt","w")
f.write("%d\n" % len(solution_4real))
for nxt in solution_4real: 
    f.write("%s\n" % slides2[nxt])
f.close()
