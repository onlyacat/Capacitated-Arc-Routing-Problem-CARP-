import random
from time import time

import copy_use

DID = DIS = DEPOT = CAPACITY = TIME = None
SIZE = 2000


def generate_cost(solution):
    cost = 0
    for route in solution[1:]:
        route_cost = 0
        demand = 0
        if len(route) == 1:
            pass
        elif len(route) == 2:
            route_cost = route_cost + DIS[DEPOT][route[1][0]][0] + DIS[route[1][1]][DEPOT][0]
            if DID.get(route[1]):
                demand = demand + DID.get(route[1])[0]
            else:
                demand = demand + DID.get((route[1][1], route[1][0]))[0]

        else:
            route_cost = route_cost + DIS[DEPOT][route[1][0]][0]
            cp = route[1][1]
            if DID.get(route[1]):
                demand = demand + DID.get(route[1])[0]
            else:
                demand = demand + DID.get((route[1][1], route[1][0]))[0]
            for y in route[2:]:
                route_cost = route_cost + DIS[cp][y[0]][0]
                cp = y[1]
                if DID.get(y):
                    demand = demand + DID.get(y)[0]
                else:
                    demand = demand + DID.get((y[1], y[0]))[0]
            route_cost = route_cost + DIS[cp][DEPOT][0]

        route[0] = [route_cost, demand]
        cost = cost + route_cost

    solution[0] = cost

    return solution


def bi_correct(p):
    for s in p:
        for route in s[1:]:
            for ti in range(1, len(route)):
                if ti == 1:
                    ori_cost = DIS[DEPOT][route[ti][0]][0] + DIS[route[ti][1]][route[ti + 1][1]][0]
                    change_cost = DIS[DEPOT][route[ti][1]][0] + DIS[route[ti][0]][route[ti + 1][1]][0]
                elif ti == len(route) - 1:
                    ori_cost = DIS[route[ti - 1][1]][route[ti][0]][0] + DIS[route[ti][1]][DEPOT][0]
                    change_cost = DIS[route[ti - 1][1]][route[ti][1]][0] + DIS[route[ti][0]][DEPOT][0]
                else:
                    ori_cost = DIS[route[ti - 1][1]][route[ti][0]][0] + DIS[route[ti][1]][route[ti + 1][0]][0]
                    change_cost = DIS[route[ti - 1][1]][route[ti][1]][0] + DIS[route[ti][0]][route[ti + 1][0]][0]
                if change_cost < ori_cost:
                    route[ti] = (route[ti][1], route[ti][0])
    return p


def cross_over(s1, s2):
    # print "Start cross over"
    # step1
    # s0 = copy.deepcopy(s1)
    s0 = copy_use.copy_solution(s1)

    # index2 = random.randint(1, len(s2) - 1)
    index2 = 1

    insert_row = s2[index2]
    replace_row = None
    index0 = -1
    for i in range(1, 100):

        # index0 = random.randint(1, len(s0) - 1)
        index0 = 3

        replace_row = s0[index0]
        if insert_row is not replace_row:
            break
        if i == 99:
            return None

    # ut = copy.deepcopy(replace_row[1:])
    ut = []
    for x in replace_row[1:]:
        ut.append(x)

    for x in insert_row[1:]:
        for y in replace_row[1:]:
            if x == y or x == (y[1], y[0]):
                ut.remove(y)
    random.shuffle(ut)
    # print "Start cross over step2"
    # step2
    need_to_del = []
    for x in insert_row[1:]:
        for route in s0[1:]:
            if replace_row is route:
                continue
            for task in route[1:]:
                if x == task or x == (task[1], task[0]):
                    if insert_row.index(x) == 1:
                        next_x = insert_row[insert_row.index(x) + 1]
                        remain_cost_x = DIS[DEPOT][next_x[0]][0]
                        dist_1 = remain_cost_x - DIS[DEPOT][x[0]][0] - DIS[x[1]][next_x[0]][0]
                    elif insert_row.index(x) == len(insert_row) - 1:
                        previous_x = insert_row[insert_row.index(x) - 1]
                        remain_cost_x = DIS[previous_x[1]][DEPOT][0]
                        dist_1 = remain_cost_x - DIS[DEPOT][x[1]][0] - DIS[x[0]][previous_x[1]][0]
                    else:
                        next_x = insert_row[insert_row.index(x) + 1]
                        previous_x = insert_row[insert_row.index(x) - 1]
                        remain_cost_x = DIS[previous_x[1]][next_x[0]][0]
                        dist_1 = remain_cost_x - DIS[previous_x[1]][x[0]][0] - DIS[x[1]][next_x[0]][0]

                    if route.index(task) == 1:
                        next_route = route[route.index(task) + 1]
                        remain_cost_task = DIS[DEPOT][next_route[0]][0]
                        dist_2 = remain_cost_task - DIS[DEPOT][task[0]][0] - DIS[task[1]][next_route[0]][0]
                    elif route.index(task) == len(route) - 1:
                        previous_r = route[route.index(task) - 1]
                        remain_cost_task = DIS[DEPOT][previous_r[1]][0]
                        dist_2 = remain_cost_task - DIS[DEPOT][task[1]][0] + DIS[task[0]][previous_r[1]][0]
                    else:
                        next_route = route[route.index(task) + 1]
                        previous_r = route[route.index(task) - 1]
                        rct = DIS[previous_r[1]][next_route[0]][0]
                        dist_2 = rct - DIS[previous_r[1]][task[0]][0] - DIS[task[1]][next_route[0]][0]

                    if dist_1 > dist_2:
                        need_to_del.append(((index0, insert_row.index(x)), x, dist_1))
                    else:
                        need_to_del.append(((s0.index(route), route.index(task)), task, dist_2))

    s0[index0] = s2[index2]

    for x in need_to_del:
        s0[x[0][0]][x[0][1]] = None

    for x in s0[1:]:
        for i in range(len(x) - 1, -1, -1):
            if not x[i]:
                x.pop(i)

    s0 = generate_cost(s0)

    # print "Start cross over step3"
    # step3
    export = 0
    while ut:
        cu_task = random.sample(ut, 1)[0]

        if DID.get(cu_task):
            get_demand = DID.get(cu_task)[0]
        else:
            get_demand = DID.get((cu_task[1], cu_task[0]))[0]

        record = []
        cost = None

        for num in [1, 2]:
            if num == 2:
                cu_task = (cu_task[1], cu_task[0])

            for p_route in s0[1:]:
                if get_demand + p_route[0][1] > CAPACITY:
                    continue

                if len(p_route) == 1:
                    cost = DIS[DEPOT][cu_task[0]][0] + DIS[cu_task[1]][DEPOT][0]
                else:
                    cost = DIS[DEPOT][cu_task[0]][0] + DIS[cu_task[1]][p_route[1][0]][0] - DIS[DEPOT][p_route[1][0]][0]

                if not record:
                    record = [cost, s0.index(p_route), 1, num]
                elif record[0] > cost:
                    record = [cost, s0.index(p_route), 1, num]

                if len(p_route) >= 2:
                    for task in p_route[2:]:
                        if p_route.index(task) == len(p_route) - 1:
                            cost = DIS[DEPOT][cu_task[1]][0] + DIS[cu_task[0]][task[1]][0] - DIS[DEPOT][task[1]][0]
                            if record[0] > cost:
                                record = [cost, s0.index(p_route), len(p_route) - 1, num]
                        else:
                            previous_route = p_route[p_route.index(task) - 1]
                            cost = DIS[previous_route[1]][cu_task[0]][0] + DIS[cu_task[1]][task[0]][0] - \
                                   DIS[previous_route[1]][task[0]][0]
                            if record[0] > cost:
                                record = [cost, s0.index(p_route), p_route.index(task), num]

        if cost is not None:
            cu_task = (cu_task[1], cu_task[0])
            ut.remove(cu_task)
            if record[3] == 2:
                cu_task = (cu_task[1], cu_task[0])
            s0[record[1]].insert(record[2], cu_task)

            s0 = generate_cost(s0)
            # for x in s0:
            #     print x
            #  print need_to_del
        else:
            export = export + 1
            if export >= 20:
                return None

    return s0


def single_insertion(ori_s):
    # print "Start single insertion"
    # s = copy.deepcopy(ori_s)
    s = copy_use.copy_solution(ori_s)
    rtu = random.sample(s[1:], 1)[0]
    u = random.sample(rtu[1:], 1)[0]
    index_u = rtu.index(u)
    demand_u = DID.get(u)[0] if DID.get(u) else DID[(u[1], u[0])][0]
    previous_u = (DEPOT, DEPOT) if index_u == 1 else rtu[index_u - 1]
    next_u = (DEPOT, DEPOT) if index_u == len(rtu) - 1 else rtu[index_u + 1]

    num = 0
    while True:
        rtv = random.sample(s[1:], 1)[0]
        v = random.sample(rtv[1:], 1)[0]
        index_v = rtv.index(v)
        if (u is not v) and (demand_u + rtv[0][1] <= CAPACITY):
            break
        num = num + 1
        if num >= 100:
            return -1
    next_v = (DEPOT, DEPOT) if index_v == len(rtv) - 1 else rtv[index_v + 1]

    remove_cost = DIS[previous_u[1]][next_u[0]][0] - DIS[previous_u[1]][u[0]][0] - DIS[u[1]][next_u[0]][0]
    add_cost1 = DIS[v[1]][u[0]][0] + DIS[u[1]][next_v[0]][0]
    add_cost2 = DIS[v[1]][u[1]][0] + DIS[u[0]][next_v[0]][0]
    if add_cost1 <= add_cost2:
        instead_u, add_cost = u, add_cost1 - DIS[v[1]][next_v[0]][0]
    else:
        instead_u, add_cost = (u[1], u[0]), add_cost2 - DIS[v[1]][next_v[0]][0]

    if remove_cost + add_cost < 0:
        s[s.index(rtu)].remove(u)
        s[s.index(rtv)].insert(index_v + 1, instead_u)
        s = generate_cost(s)
        return s
    else:
        return 0


def swap(ori_s):
    s = copy_use.copy_solution(ori_s)
    rtu = random.sample(s[1:], 1)[0]
    u = random.sample(rtu[1:], 1)[0]
    index_u = rtu.index(u)
    demand_u = DID.get(u)[0] if DID.get(u) else DID[(u[1], u[0])][0]
    previous_u = (DEPOT, DEPOT) if index_u == 1 else rtu[index_u - 1]
    next_u = (DEPOT, DEPOT) if index_u == len(rtu) - 1 else rtu[index_u + 1]

    num = 0
    while True:
        rtv = random.sample(s[1:], 1)[0]
        v = random.sample(rtv[1:], 1)[0]
        index_v = rtv.index(v)
        if (u is not v) and (demand_u + rtv[0][1] <= CAPACITY):
            break
        num = num + 1
        if num >= 100:
            return -1
    previous_v = (DEPOT, DEPOT) if index_v == 1 else rtv[index_v - 1]
    next_v = (DEPOT, DEPOT) if index_v == len(rtv) - 1 else rtv[index_v + 1]

    remove_cost_u = DIS[previous_u[1]][u[0]][0] + DIS[u[1]][next_u[0]][0]
    remove_cost_v = DIS[previous_v[1]][v[0]][0] + DIS[v[1]][next_v[0]][0]

    insert_cost_v = DIS[previous_u[1]][v[0]][0] + DIS[v[1]][next_u[0]][0]
    insert_cost_v_swap = DIS[previous_u[1]][v[1]][0] + DIS[v[0]][next_u[0]][0]
    if insert_cost_v > insert_cost_v_swap:
        v = (v[1], v[0])
        insert_cost_v = insert_cost_v_swap

    insert_cost_u = DIS[previous_v[1]][u[0]][0] + DIS[u[1]][next_v[0]][0]
    insert_cost_u_swap = DIS[previous_v[1]][u[1]][0] + DIS[u[0]][next_v[0]][0]
    if insert_cost_u > insert_cost_u_swap:
        u = (u[1], u[0])
        insert_cost_u = insert_cost_u_swap
    if insert_cost_u + insert_cost_v - remove_cost_u - remove_cost_v < 0:
        rtu[index_u] = v
        rtv[index_v] = u
        s = generate_cost(s)
        return s
    else:
        return 0


def search_loop(solution, demand_in_dict, depot, distance, capacity, cnum, mnum, s_time, t_time):
    global DIS, DEPOT, CAPACITY, DID, TIME
    DEPOT = depot
    DIS = distance
    CAPACITY = capacity
    DID = demand_in_dict
    TIME = t_time
    pool = bi_correct(solution)
    #
    # s0 = cross_over(solution[0], solution[1], demand_in_dict)

    for i in range(1, cnum):
        if time() - s_time > float(TIME - 3):
            pool.sort()
            break
        s = random.sample(solution, 2)
        s0 = cross_over(copy_use.copy_solution(s[0]), copy_use.copy_solution(s[1]))
        # s0 = cross_over(copy.deepcopy(s[0]), copy.deepcopy(s[1]), demand_in_dict)
        if not s0:
            continue
        if s0[0] > pool[int(len(pool)) / 2][0]:
            continue
        pool.append(s0)

        for j in range(1, mnum):
            s = single_insertion(s0)
            if s != 0 and s != -1:
                pool.append(s)
            s = swap(s0)
            if s != 0 and s != -1:
                pool.append(s)

        pool.sort()
        if len(pool) > SIZE:
            pool = pool[0:SIZE]

    return bi_correct(pool)
