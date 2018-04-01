def copy_demand_list(input_list):
    new_list = []
    for x in input_list:
        new_list.append(x)
    return new_list


def copy_solution(solution):
    new_solution = [solution[0]]

    for route in solution[1:]:
        new_route = [route[0]]

        for task in route[1:]:
            new_route.append(task)

        new_solution.append(new_route)

    return new_solution
