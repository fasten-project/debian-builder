import sys
import json
import colorama
from colorama import Fore, Style
from pprint import pprint


def main(path1, path2, gnode=None):
    with open(path1, 'r') as f:
        data1 = json.load(f)
    with open(path2, 'r') as f:
        data2 = json.load(f)
    deps1 = set()
    deps2 = set()
    for x in data1['depset']:
        if isinstance(x, list):
            for i in x:
                deps1.add(i['product'])
        else:
            deps1.add(x['product'])
    for x in data2['depset']:
        if isinstance(x, list):
            for i in x:
                deps2.add(i['product'])
        else:
            deps2.add(x['product'])
    cg1 = {}
    cg2 = {}
    t1 = set()
    t2 = set()
    counter1 = 0
    counter2 = 0
    for edge in data1['graph']:
        t1.add(tuple(edge))
        if edge[0] in cg1.keys():
            cg1[edge[0]].append(edge[1])
        else:
            cg1[edge[0]] = [edge[1]]
    for edge in data2['graph']:
        t2.add(tuple(edge))
        if edge[0] in cg2.keys():
            cg2[edge[0]].append(edge[1])
        else:
            cg2[edge[0]] = [edge[1]]
    if gnode is not None:
        pprint(cg1[gnode])
        pprint(cg2[gnode])
        sys.exit()
    print(Fore.GREEN)
    for node, edges in cg1.items():
        if node not in cg2.keys():
            print(node)
            counter1 += len(edges)
            for e in edges:
                print("\t" + e)
        else:
            temp = [x for x in edges if x not in cg2[node]]
            if len(temp) != 0:
                print(Style.RESET_ALL + node + Fore.GREEN)
                for e in temp:
                    print("\t" + e)
                    counter1 += 1
    print(Fore.RED)
    for node, edges in cg2.items():
        if node not in cg1.keys():
            print(node)
            counter2 += len(edges)
            for e in edges:
                print("\t" + e)
        else:
            temp = [x for x in edges if x not in cg1[node]]
            if len(temp) != 0:
                print(Style.RESET_ALL + node + Fore.RED)
                for e in temp:
                    print("\t" + e)
                    counter2 += 1
    print(Style.RESET_ALL)
    print("Dependencies in {} and not in {}: {}".format(
        path1, path2, deps1-deps2)
    )
    print("Dependencies in {} and not in {}: {}".format(
        path2, path1, deps2-deps1)
    )
    print("Total edges {}: {}".format(path1, len(t1)))
    print("Total edges {}: {}".format(path2, len(t2)))
    print("Common edges: {}".format(len(t1 & t2)))
    print("Edges in {} but not in {}: {}".format(path1, path2, counter1))
    print("Edges in {} but not in {}: {}".format(path2, path1, counter2))


if __name__ == "__main__":
    gnode = None
    if len(sys.argv) < 3:
        print("You should provide 2 paths")
        sys.exit()
    if len(sys.argv) == 4:
        gnode = sys.argv[3]
    main(sys.argv[1], sys.argv[2], gnode)
