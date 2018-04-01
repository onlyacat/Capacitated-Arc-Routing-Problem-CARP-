# -*- coding: UTF-8 -*-

import getopt
import heapq as hq
import multiprocessing
import re
import sys
from collections import defaultdict
from time import time

from main_search import search_loop
from path_scanning import generate_path

CPU = VERTICES = CAPACITY = DEPOT = TOTAL_COST = VEHICLES = DEMAND_NUM = RATIO = -1
SEED = EDGES = DIL = DID = DIS = None
TIME = None
NAME = None


def get_opt(argv):
    global NAME, TIME, SEED
    if len(argv) == 0:
        raise TypeError
    NAME = argv.pop(0)
    try:
        opts, args = getopt.getopt(argv, "ht:s:")
    except getopt.GetoptError:
        print 'carp_solver.py <fileName> -t <time> -s <seed>'
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print 'carp_solver.py <fileName> -t <time> -s <seed>'
            sys.exit()
        elif opt == "-t":
            TIME = int(arg)
        elif opt == "-s":
            SEED = str(arg)

    if NAME is None or TIME is None or SEED is None:
        raise TypeError


def input_data():
    global VERTICES, CAPACITY, DEPOT, TOTAL_COST, VEHICLES, DEMAND_NUM, EDGES, DIL, DID, RATIO, CPU
    CPU = multiprocessing.cpu_count()
    if CPU not in range(1, 20):
        CPU = 1
    if CPU > 8:
        CPU = 8

    # with open('data/gdb10.dat', 'r') as content:
    with open(NAME, 'r') as content:
        given_file = content.readlines()

    arr = []
    for x in given_file:
        arr.append(re.split(" *:*", x.strip()))

    VERTICES = int(arr[1][2]) + 1
    CAPACITY = int(arr[6][2])
    DEPOT = int(arr[2][2])
    TOTAL_COST = int(arr[7][6])
    VEHICLES = int(arr[5][2])
    EDGES = defaultdict(list)
    DIL = []
    DID = defaultdict()
    for x in arr[9:len(arr) - 1]:
        EDGES[int(x[0])].append((int(x[2]), int(x[1])))
        EDGES[int(x[1])].append((int(x[2]), int(x[0])))
        if int(x[3]) != 0:
            DIL.append((int(x[0]), int(x[1]), int(x[3]), int(x[2])))
            DID[(int(x[0]), int(x[1]))] = (int(x[3]), int(x[2]))
            DEMAND_NUM = DEMAND_NUM + int(x[3])

    RATIO = VEHICLES / DEMAND_NUM


def dijkstra_raw(from_node, to_node):
    q, seen = [(0, from_node, ())], set()
    while q:
        (cost, v1, path) = hq.heappop(q)
        if v1 not in seen:
            seen.add(v1)
            path = (v1, path)
            if v1 == to_node:
                return cost, path
            for c, v2 in EDGES.get(v1, ()):
                if v2 not in seen:
                    hq.heappush(q, (cost + c, v2, path))
    return 65535, []


def dijkstra(from_node, to_node):
    len_shortest_path = -1
    ret_path = []
    length, path_queue = dijkstra_raw(from_node, to_node)
    if len(path_queue) > 0:
        len_shortest_path = length  # 1. Get the length firstly;
        # 2. Decompose the path_queue, to get the passing nodes in the shortest path.
        left = path_queue[0]
        ret_path.append(left)  # 2.1 Record the destination node firstly;
        right = path_queue[1]
        while len(right) > 0:
            left = right[0]
            ret_path.append(left)  # 2.2 Record other nodes, till the source-node.
            right = right[1]
        ret_path.reverse()  # 3. Reverse the list finally, to make it be normal sequence.
    return len_shortest_path, ret_path


def get_distance():
    global DIS
    dis = [(65535,)]
    for x in range(1, VERTICES):
        dis_t = [65535]
        for y in range(1, VERTICES):
            if x < y:
                dis_t.append(dijkstra(x, y))
            elif x > y:
                dis_t.append(dis[y][x])
            else:
                dis_t.append([0, 0])
        dis.append(dis_t)
    DIS = dis


def ini_ps(num):
    pool = multiprocessing.Pool()
    result = []
    for i in xrange(CPU):
        result.append((pool.apply_async(generate_path, args=(CAPACITY, DIL, DIS, DEPOT, RATIO, num, DID))))

    pool.close()
    pool.join()

    sp = []
    for x in result:
        sp.extend(x.get())

    return sp


def ini_search(sp, cnum, mnum, st):
    pool = multiprocessing.Pool()
    result = []
    for i in xrange(CPU):
        result.append((pool.apply_async(search_loop, args=(sp, DID, DEPOT, DIS, CAPACITY, cnum, mnum, st, TIME))))

    pool.close()
    pool.join()

    for x in result:
        # print len(sp)
        sp.extend(x.get())

    return sp


def format_output(s_fin):
    s = "s "
    for route in s_fin[1:]:
        s = s + "0,"
        for task in route[1:]:
            s = s + str(task).replace(" ", "") + ","
        s = s + "0,"

    print s.strip(',')
    print "q %d" % (s_fin[0] + TOTAL_COST)


def control_spending_time(st):
    start_scanning_test = time()
    solution_pool = ini_ps(10000 / CPU)
    end_scanning_test = time()
    spending_in_scanning_test = end_scanning_test - start_scanning_test
    # print spending_in_scanning_test

    can_use_time = int((0.4 * TIME - spending_in_scanning_test) * 10000 / spending_in_scanning_test)
    # print "THE NUM IN MAIN SCANNING IS %d" % can_use_time
    if int(can_use_time / CPU) > 100:
        solution_pool_main = ini_ps(int(can_use_time / CPU))
        solution_pool.extend(solution_pool_main)
        solution_pool.sort()

    end_scanning_main = time()

    spending_in_scanning = end_scanning_main - start_scanning_test

    # print spending_in_scanning
    # print "THE BEST IN SCANNING IS %d" % (solution_pool[0][0] + TOTAL_COST)

    start_searching_test = time()
    new_pool = ini_search(solution_pool, 999999, 200, st)
    new_pool.sort()
    end_searching_test = time()
    spending_in_searching_test = end_searching_test - start_searching_test
    # print spending_in_searching_test
    # print "THE BEST IN SEARCHING IS %d" % (new_pool[0][0] + TOTAL_COST)
    format_output(new_pool[0])


if __name__ == '__main__':
    try:
        start = time()

        get_opt(sys.argv[1:])

        input_data()

        get_distance()
        # sp = generate_path(CAPACITY, DIL, DIS, DEPOT, RATIO, 2000, DID)
        # search_loop(sp, DID, DEPOT, DIS, CAPACITY, 1000, 100, start, TIME)
        control_spending_time(start)
        # generate_path(CAPACITY, DIL, DIS, DEPOT, RATIO, 20000, DID)
        # end = time()
        # print end - start

    except TypeError:
        print 'carp_solver.py <fileName> -t <time> -s <seed>'
    except ValueError:
        print 'carp_solver.py <fileName> -t <time> -s <seed>'
    except IOError:
        print "INVALID INPUT FILE"
