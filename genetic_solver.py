import random
import datetime

PARAMETERS = {'population_size': 100, 'mutation_possibility': 0.25, 'number_of_generations': 30000, 'survivor_size': 5}
problem_instance = None
dbg = True


def debug_print(*args, **kwargs):
    if dbg:
        print(*args, **kwargs)


class Validity:
    def __init__(self, valid=True, problem_at_day=None, problem_tool=None, involved_requests=None):
        self.valid = valid
        self.day = problem_at_day
        self.tool = problem_tool
        self.involved_requests = involved_requests

    def __bool__(self):
        return self.valid


class InOut:
    def __init__(self, in_=0, out_=0):
        self.in_ = in_
        self.out_ = out_

    def add_in(self, value):
        self.in_ += value

    def add_out(self, value):
        self.out_ += value


class Candidate:
    def __init__(self, day_list, fitness_=None):
        # ctor
        self.day_list = day_list
        if fitness_ is not None:
            self.fit = fitness_
        else:
            self.fit = self.fitness_heuristic()

    def __str__(self):
        return 'CANDIDATE (' + str(self.fit) + '): ' + str(self.day_list)

    def __eq__(self, other):
        return self.day_list == other.day_list

    def get_tool_usages(self):
        day_list = self.day_list
        # usage:
        # Key:   TOOL ID
        # Value: List of length = len(day_list),
        #         each index denotes how many tools are required at that day
        usage = {}
        for tool_id in problem_instance['tools'].keys():
            usage[tool_id] = [0 for _ in day_list]

        # walk through every day
        for (idx, req_list) in enumerate(day_list):

            # for each day, walk through every request on that day
            for _req in req_list:

                # calculate the variables that we need
                request = problem_instance['requests'][_req['id']]
                tool_id = request.tool_id
                delivery_amount = 0
                fetch_amount = 0

                # if it's the beginning of the request (i.e. delivery), add to the delivery amount
                # else to the fetch amount
                if not _req['return']:
                    delivery_amount = request.num_tools
                else:
                    fetch_amount = request.num_tools

                # assuming that we are lucky, we can fetch tools and directly deliver them to another customer
                usage[tool_id][idx] += delivery_amount
                usage[tool_id][idx] -= fetch_amount

                # don't forget to take those tools into account which are still at a customer's place
                if idx > 0:
                    usage[tool_id][idx] += usage[tool_id][idx - 1]

        return usage

    def get_problems_for_tool(self, tool_id):
        """Calculate a list of problems for the

        :param tool_id:
        :return:
        """
        usages = self.get_tool_usages()[tool_id]
        available = problem_instance['tools'][tool_id].num_available
        problems = []

        for (day, usage) in enumerate(usages):
            involved_requests = []
            uses = usage

            for request in problem_instance['requests']:
                if request.first_day <= day <= request.last_day:
                    involved_requests.append(request)

            if usage > available:
                problems.append((day, uses, available, involved_requests))

        return problems

    def is_valid(self):
        usages = self.get_tool_usages()

        for tool_id in problem_instance['tools'].keys():
            available = problem_instance['tools'][tool_id].num_available

            for usage in usages[tool_id]:
                if usage > available:
                    return False

        return True

    def fitness_heuristic(self):
        max_cars = 0
        sum_cars = 0
        sum_distance = 0
        tsp_per_day  = []

        tools_in_out   = [[] for _ in range(problem_instance['days'])]
        optimistic_max = {}

        for (day_index, requests_on_day) in enumerate(self.day_list):
            cars = []

            # initialise the deliver/fetch tuple
            for tool_key in problem_instance['tools'].keys():
                tools_in_out[day_index][tool_key] = InOut(0, 0)
                optimistic_max[tool_key] = 0

            # calculate the deliver/fetch tuple for each day
            for request in requests_on_day:
                req = request
                tool_id = req.tool_id
                req = problem_instance['requests'][request['id']]
                in_out = tools_in_out[day_index][tool_id]

                if req['return']:
                    in_out.add_in(req.num_tools)
                else:
                    in_out.add_out(req.num_tools)

        for (day_index, requests_on_day) in enumerate(self.day_list):
            pass
            for request in requests_on_day:
                req = problem_instance['requests'][request['id']]

                # TODO get no. cars, get tsp
                # - auslastung der autos
                # - nearest neighbour (+ depotbesuche dazwischen erlaubt)
                # - tools mit dem gleichen typ mit dem gleichen auto machen wenn möglich (=> weniger tools nötig)
                break

            sum_cars += len(cars)
            if len(cars) > max_cars:
                max_cars = len(cars)

        max_tools = {}#[0 for _ in range(len(problem_instance['tools']))]
        for k in problem_instance['tools'].keys():
            max_tools[k] = 0

        for tsp in tsp_per_day:
            for request in tsp:
                # TODO
                break

        sum_tool_costs = 0
        for tool in max_tools:
            break
            # TODO sum_tool_costs += tool.max * problem_instance['tools'][tool.id].price

        return 0
        # return max_cars * cars_per_day + \
        #        sum_cars * cars_per_day + \
        #        sum_distance * distance_cost + \
        #        sum_tool_costs

    def mutate(self):
        """Perform random mutations on Candidate a

        :return:
        """

        r = random.random()

        if r < PARAMETERS['mutation_possibility']:
            # TODO
            return


def initial_population(population_size):
    """Create the initial population for the genetic algorithm

    :return: a list of candidates
    """

    # for each request, pick a random starting day and the corresponding end day
    population = []
    for i in range(0, population_size):
        day_list = [[] for _ in range(problem_instance['days'])]

        for key, request in problem_instance['requests'].items():
            start_day = random.randrange(request.first_day, request.last_day + 1) # randrange excludes the stop point of the range.
            day_list[start_day]                   .append({'id': request.id, 'return': False})
            day_list[start_day + request.num_days].append({'id': request.id, 'return': True })

        # usage:
        # Key:   TOOL ID
        # Value: List of length = len(day_list),
        #         each index denotes how many tools are required at that day
        usage = {}
        available = {}
        for tool_id in problem_instance['tools'].keys():
            usage[tool_id] = [0 for _ in day_list]
            available[tool_id] = problem_instance['tools'][tool_id].num_available

        # walk through every day
        for (idx, req_list) in enumerate(day_list):

            # for each day, walk through every request on that day
            for _req in req_list:

                # calculate the variables that we need
                request = problem_instance['requests'][_req['id']]
                tool_id = request.tool_id
                delivery_amount = 0
                fetch_amount = 0

                # if it's the beginning of the request (i.e. delivery), add to the delivery amount
                # else to the fetch amount
                if not _req['return']:
                    delivery_amount = request.num_tools
                else:
                    fetch_amount = request.num_tools

                # assuming that we are lucky, we can fetch tools and directly deliver them to another customer
                usage[tool_id][idx] += delivery_amount
                usage[tool_id][idx] -= fetch_amount

                # don't forget to take those tools into account which are still at a customer's place
                if idx > 0:
                    usage[tool_id][idx] += usage[tool_id][idx - 1]

                if usage[tool_id][idx] > available[tool_id]:
                    pass
                    # TODO invalid solution
                    # TODO worsen fitness function? set valid flag to false?


        population.append(Candidate(day_list))
    return population


def combine(a, b):
    """Let Candidates a and b create a child element, inheriting some characteristics of each

    :param a:
    :param b:
    :return:
    """

    # TODO recombination has to be smart (check if some requests are now duplicated or missing,
    # TODO or the start/end day requirement is violated
    # TODO dunno if this kind of recombination is still smart, or if there would be some better way
    combined_content = ''
    for idx in range(0, 10):
        r = random.random()
        if r < 0.5:
            combined_content += a.content[idx]
        else:
            combined_content += b.content[idx]

    return Candidate(combined_content)


def find_mating_pair(values, scale, blocked_values=None):
    """From the values list, find a pair which is not in the blocked_list.

    :param values:
    :param scale:
    :param blocked_values:
    :return: A tuple of Candidates
    """

    if len(values) < 2:
        raise Exception('Population too small')

    if blocked_values is None:
        blocked_values = []

    val_0 = get_random_candidate(values, scale)
    val_1 = None

    while (val_1 is None) or (val_0 == val_1) \
            or (val_0, val_1) in blocked_values or (val_1, val_0) in blocked_values:
        val_1 = get_random_candidate(values, scale)

    return (val_0[2], val_1[2])


def get_random_candidate(values, scale):
    """Fetch a random candidate from the supplied values list.

    Generate a random value R in the range [0, SCALE) and fetch that element from the values list
    where LOWER <= R < UPPER.

    :param values: A list containing triples of the form (LOWER, UPPER, ELEMENT)
    :param scale: The sum of all fitness values
    :return: An element from the values list
    """

    r = random.random() * scale
    for v in values:
        # v[0] -> LOWER
        # v[1] -> UPPER
        if v[0] <= r < v[1]:
            return v


def make_fitness_range(values):
    """Create a list containing triples of the form (LOWER, UPPER, ELEMENT)

    :param values:
    :return:
    """
    great_range = []
    upper = 0

    for elem in values:
        lower = upper
        upper = lower + elem.fit
        great_range.append((lower, upper, elem))

    return great_range


def solve_problem(problem):
    start = datetime.datetime.now()
    print('Starting now: ' + start.isoformat())

    global problem_instance
    problem_instance = problem

    #create initial population
    population = initial_population(PARAMETERS['population_size'])
    population = sorted(population, key=lambda p: p.fit)
    population_size = len(population)
    #debug_print([str(p) for p in population])
    [print(str(p) + '\n') for p in population[0].day_list]

    '''for i in range(0, 30000):
        debug_print ('\nIteration: =====' + str(i) + '=======')
        sum_fitness_values = functools.reduce(operator.add, [p.fit for p in population], 0)
        # debug_print(sum_fitness_values)

        fitness_range = make_fitness_range(population)
        
        # crossover
        # select crossover candidates (candidates with higher fitness have a higher chance to get reproduced)
        (one, two) = find_mating_pair(fitness_range, sum_fitness_values)

        combined = combine(one, two)

        # mutate (happens randomly)
        combined.mutate()

        if combined in population:
            debug_print('WHAT IS HAPPENING')
            continue

        debug_print('1: ' + str(one))
        debug_print('2: ' + str(two))
        debug_print('Combined: ' + combined.content)

        # select survivors (the best ones survive)
        population.append(combined)
        population = sorted(population, key=lambda p: p.fit)[-population_size:]
        debug_print('Population after mutation: ' + str([str(p) for p in population]))
        debug_print('Best: ' + str(population[-1:][0]))
        debug_print('Worst: ' + str(population[0]))
'''

    end = datetime.datetime.now()
    print('Done: ' + end.isoformat())
    print('Took me: ' + str((end - start).seconds) + 's')


