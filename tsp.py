
#!/usr/bin/python3

import sys

# structure de cette liste:
# (id, orientation, tag0, tag1, tag2, ..)
photos = []
keywords = {}

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
#print(photos)

import math
import random
from gurobipy import *


from collections import defaultdict
valid_edges = defaultdict(list)

# Callback - use lazy constraints to eliminate sub-tours

def subtourelim(model, where):
  if where == GRB.callback.MIPSOL:
    selected = []
    # make a list of edges selected in the solution
    for i in range(n):
      sol = model.cbGetSolution([model._vars[i,j] for j in valid_edges[i]])
      selected += [(i,j) for j in valid_edges[i] if sol[j] > 0.5]
    # find the shortest cycle in the selected edge list
    tour = subtour(selected)
    if len(tour) < n:
      # add a subtour elimination constraint
      expr = 0
      for i in range(len(tour)):
        for j in range(i+1, len(tour)):
          expr += model._vars[tour[i], tour[j]]
      model.cbLazy(expr <= len(tour)-1)


# Given a list of edges, finds the shortest subtour

def subtour(edges):
  visited = [False]*n
  cycles = []
  lengths = []
  selected = [[] for i in range(n)]
  for x,y in edges:
    selected[x].append(y)
  while True:
    current = visited.index(False)
    thiscycle = [current]
    while True:
      visited[current] = True
      neighbors = [x for x in selected[current] if not visited[x]]
      if len(neighbors) == 0:
        break
      current = neighbors[0]
      thiscycle.append(current)
    cycles.append(thiscycle)
    lengths.append(len(thiscycle))
    if sum(lengths) == n:
      break
  return cycles[lengths.index(min(lengths))]


n = len(photos)

m = Model()

def compute_score(p1, p2):
    tags1 = set(p1[2])
    tags2 = set(p2[2])
    return min(len(tags1 & tags2), len(tags1 - tags2), len(tags2 - tags1))

# find interesting distances between photos

score_threshold = 5
distances = {}


index = defaultdict(list)

from itertools import combinations
import pickle
import os

if len(sys.argv) == 1:
    prefix = "b"
else:
    prefix = sys.argv[1]
    print("prefix:",prefix)

if not os.path.exists(prefix + "_index.pickle"):
    for (i,p) in enumerate(photos):
        tags = p[2]
        for tag1 in tags:
            for tag2 in tags:
                if tag1 < tag2:
                    index[(tag1,tag2)] += [i]
    pickle_file = open(prefix + "_index.pickle","wb")
    pickle.dump(index,pickle_file)
    pickle_file.close()

    print("b index computed")

if not os.path.exists(prefix + "_distances.pickle"):
    pickle_file = open(prefix + "_index.pickle","rb")
    index = pickle.load(pickle_file)
    pickle_file.close()
    print("b index loaded")


    def close_sets(tags):
        candidates = []
        for tag1 in tags:
            for tag2 in tags:
                if tag1 < tag2:
                    if (tag1, tag2) in index:
                        candidates += index[(tag1,tag2)]
        return set(candidates)


    nb_edges = 0
    for i,p1 in enumerate(photos):
        if i % 500 == 0: print(i,"edges so far:",nb_edges)
        tags = p1[2]
        for j in close_sets(tags):
            if j > i: continue # will be symmetrical
            p2 = photos[j]
            #print(len(close_sets(tags)),"indsteadof 8000")
            #for j, p2 in enumerate(photos):
            score = compute_score(p1,p2)
            if score > score_threshold:
                distances[(i,j)] = score
                nb_edges += 1

    import pickle
    pickle_file = open(prefix + "_distances.pickle","wb")
    pickle.dump(distances,pickle_file)
    pickle_file.close()
    print(prefix + " distances computed,",nb_edges,"edges",len(distances),"distances")

import pickle
pickle_file = open(prefix + "_distances.pickle","rb")
distances = pickle.load(pickle_file)
pickle_file.close()
print(prefix + " distances loaded",len(distances))

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
    vars[i,j] = m.addVar(obj=distance_func(i, j), vtype=GRB.BINARY,name='e'+str(i)+'_'+str(j))
    vars[j,i] = vars[i,j]
m.update()

#print(distances)
# dunno
for i in range(n):
    vars[i,i] = m.addVar(obj=distance_func(i, i), vtype=GRB.BINARY,name='e'+str(i)+'_'+str(i))

print("variables created")


# Add degree-2 constraint, and forbid loops

for i in range(n):
  m.addConstr(quicksum(vars[i,j] for j in valid_edges[i] ) <= 2)
  vars[i,i].ub = 0

m.update()

print("constraints made")

# Optimize model

m._vars = vars
m.params.LazyConstraints = 1
#m.optimize(subtourelim)

m.modelSense = GRB.MAXIMIZE
m.optimize()

solution = m.getAttr('x', vars)
#print("solution",solution)
selected = [(i,j) for (i,j) in distances if solution[i,j] > 0.5]
#assert len(subtour(selected)) == n
print("selected",selected)
#print(len(subtour(selected)))
#print(subtour(selected))

# walk the solution

import networkx as nx

g = nx.Graph()

for e in selected:
    g.add_edge(*e)

print("number connected components:", nx.number_connected_components(g))

f = open("sol_" + prefix + ".txt","w")
nb_nodes = len(g.nodes())
f.write("%d\n" % nb_nodes)

for i,connected_component_2 in enumerate(nx.connected_component_subgraphs(g)):
    connected_component = nx.Graph(connected_component_2)
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
        print(i,extremity,len(connected_component))
        nxt = extremity
        f.write("%d\n" % nxt)
        while True:
            if len(connected_component.nodes()) == 0:
                done = True
                break
            nxt_set = set(connected_component.neighbors(nxt))
            connected_component.remove_node(nxt)
            if len(nxt_set) == 0:
                #start again with a new node
                break
            print("deleting",nxt, "next one is",list(nxt_set)[0])
            print(nxt in connected_component.nodes())
            nxt = list(nxt_set)[0]
            print(i,nxt)
            f.write("%d\n" % nxt)
f.close()


