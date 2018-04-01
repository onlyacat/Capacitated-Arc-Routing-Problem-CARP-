import random

import copy_use

DID = DIS = None
RATIO = DEPOT = CAPACITY = -1


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


def random_judge(p_demand, point, current_capacity):
    pool = []
    for x in p_demand:
        if point == (x[0] or x[1]) and x[2] + current_capacity <= CAPACITY:
            pool.append(x)

    if pool:
        index = random.randint(0, len(pool) - 1)
        if pool[index][0] == point:
            temp_node = (point, pool[index][1])
        else:
            temp_node = (point, pool[index][0])
        return temp_node, 0, pool[index]
    else:
        for x in p_demand:
            if x[2] + current_capacity <= CAPACITY:
                if DIS[point][x[0]][0] < DIS[point][x[1]][0]:
                    node_value = DIS[point][x[0]][0]
                    temp_node = (x[0], x[1])
                else:
                    node_value = DIS[point][x[1]][0]
                    temp_node = (x[1], x[0])
                pool.append((temp_node, node_value, x))

        if pool:
            index = random.randint(0, len(pool) - 1)
            return pool[index]
        else:
            return []


def simply_judge(p_demand, point, current_capacity):
    current_change = []
    current_node = []
    for x in p_demand:
        if x[2] + current_capacity <= CAPACITY:
            if DIS[point][x[0]][0] == 0:
                node_value = 0
                temp_node = (point, x[1])
            elif DIS[point][x[1]][0] == 0:
                node_value = 0
                temp_node = (point, x[0])
            elif DIS[point][x[0]][0] < DIS[point][x[1]][0]:
                node_value = DIS[point][x[0]][0]
                temp_node = (x[0], x[1])
            else:
                node_value = DIS[point][x[1]][0]
                temp_node = (x[1], x[0])
            current_node.append((temp_node, node_value, x))
            current_change.append(float((node_value + x[3]) / x[2]))

    if current_change:
        x = current_change.index(min(current_change))
        return current_node[x]
    else:
        return []


def weight_choice(weight):
    t = random.randint(0, sum(weight) - 1)
    for i, val in enumerate(weight):
        t -= val
        if t < 0:
            return i


def path_scanning(d):
    p_demand = copy_use.copy_demand_list(d)
    # p_demand = copy.deepcopy(d)
    current_point = DEPOT
    path = [0]
    current_capacity = 0
    route = [[0, 0]]
    route_cost = 0
    while p_demand:
        if random.randint(0, 5) == 0:
            current_node = random_judge(p_demand, current_point, current_capacity)
        else:
            current_node = simply_judge(p_demand, current_point, current_capacity)

        ratio = int(RATIO * 100)
        end = weight_choice([ratio, 100 - ratio])

        if (not current_node) or end == 0:
            path.append(route)
            route = [[0, 0]]
            current_point = DEPOT
            current_capacity = 0
            route_cost = 0
        else:
            route.append(current_node[0])
            route_cost = route_cost + current_node[1]
            current_capacity = current_capacity + current_node[2][2]
            current_point = current_node[0][1]
            p_demand.remove(current_node[2])

    path.append(route)

    path = generate_cost(path)

    return path


def generate_path(capacity, d, distance, depot, ratio, num, did):
    global CAPACITY, DIS, DEPOT, RATIO, DID
    CAPACITY, DIS, DEPOT, RATIO, DID = capacity, distance, depot, ratio, did
    population_pool = []
    while len(population_pool) < num:
        population_pool.append(path_scanning(d))
    return population_pool

    # a = [0, [[0,0],(1, 11), (11, 4), (4, 2), (2, 7), (7, 4), (4, 6)],
    #      [[0, 0], (1, 10), (10, 12), (12, 8), (8, 9), (9, 3), (3, 4), (4, 1)],
    #      [[0, 0], (1, 2), (2, 5), (5, 6), (6, 11), (11, 12), (10, 9), (9, 1)],
    #      [[0, 0], (1, 5), (5, 7), (2, 3), (3, 8), (8, 1)]]
    #
    # b = generate_cost(a)
    # print b
