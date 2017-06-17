#!/usr/bin/env python3

import sys
import argparse
import json
import math
import genetic_solver


class Tool:
    def __init__(self, id, size, num_availabe, cost):
        # ctor
        self.id = int(id)
        self.size = int(size)
        self.num_available = int(num_availabe)
        self.cost = int(cost)

    @classmethod
    def create_from_line(self, line):
        line_splitted = line.split('\t')
        return self(*line_splitted) # splat operator, for unpacking argument lists

    def __repr__(self):
        return 'TOOL #{}: size={}; num_available={}; cost={};'.format(self.id, self.size, self.num_available, self.cost)


class Customer:
    def __init__(self, id, x, y):
        # ctor
        self.id = int(id)
        self.x = int(x)
        self.y = int(y)

    @classmethod
    def create_from_line(self, line):
        line_splitted = line.split('\t')
        return self(*line_splitted) # splat operator, for unpacking argument lists

    def __repr__(self):
        return 'CUSTOMER #{}: x={}; y={};'.format(self.id, self.x, self.y)


class Request:
    def __init__(self, id, customer_id, first_day, last_day, num_days, tool_id, num_tools):
        # ctor
        self.id = int(id)
        self.customer_id = int(customer_id)
        self.first_day = int(first_day) - 1 # for convenience when working with arrays of day-numbers
        self.last_day  = int(last_day)  - 1 # for convenience when working with arrays of day-numbers
        self.num_days = int(num_days)
        self.tool_id = int(tool_id)
        self.num_tools = int(num_tools)

    @classmethod
    def create_from_line(self, line):
        line_splitted = line.split('\t')
        return self(*line_splitted) # splat operator, for unpacking argument lists

    def __repr__(self):
        return 'REQUEST #{}: customer_id={}; first_day={}; last_day={}; num_days={}; tool_id={}; num_tools={};'\
            .format(self.id, self.customer_id, self.first_day, self.last_day, self.num_days, self.tool_id, self.num_tools)

#TODO REMOVE ME?
class Problem:
    def __init__(self, tools=None, customers=None, requests=None):
        self.tools = tools
        self.customers = customers
        self.requests = requests

        if self.tools is None:
            self.tools = {}

        if self.customers is None:
            self.customers = {}

        if self.requests is None:
            self.requests = {}


def main(argv=None):
    parser = argparse.ArgumentParser(description='Genetic algorithm for the VeRoLog Solver Challenge 2017')
    parser.add_argument('file', help='problem instance, txt-file')
    # TODO add more arguments? (algorithm parameters?)
    args = parser.parse_args(argv)

    #read the file
    with open(args.file, 'r') as f:
        lines = [line.strip() for line in f.readlines() if line.strip()]

    problem = {}
    problem['tools'] = {}
    problem['customers'] = {}
    problem['requests'] = {}
    state = 'none'

    # decide what information to save for each line
    for line in lines:
        if line.startswith('DATASET'):
            problem['dataset'] = getValueFromLine(line)
        elif line.startswith('NAME'):
            problem['name'] = getValueFromLine(line)

        elif line.startswith('DAYS'):
            problem['days'] = int(getValueFromLine(line))
        elif line.startswith('CAPACITY'):
            problem['capacity'] = int(getValueFromLine(line))
        elif line.startswith('MAX_TRIP_DISTANCE'):
            problem['max_trip_distance'] = int(getValueFromLine(line))
        elif line.startswith('DEPOT_COORDINATE'):
            problem['depot_coordinate'] = int(getValueFromLine(line))

        elif line.startswith('VEHICLE_COST'):
            problem['vehicle_cost'] = int(getValueFromLine(line))
        elif line.startswith('VEHICLE_DAY_COST'):
            problem['vehicle_day_cost'] = int(getValueFromLine(line))
        elif line.startswith('DISTANCE_COST'):
            problem['distance_cost'] = int(getValueFromLine(line))

        elif line.startswith('TOOLS'):
            state = 'tools'
        elif line.startswith('COORDINATES'):
            state = 'customers' # rename coordinates to customers, because it's easier to understand
        elif line.startswith('REQUESTS'):
            state = 'requests'
        elif line.startswith('DISTANCE'):
            state = 'distance' # needed => so that distance matrix lines are not interpreted as request lines

        elif line.strip() != '':
            if state == 'tools':
                tool = Tool.create_from_line(line)
                problem['tools'].update({tool.id:tool}) # dictionary entry; key = tool.id, value = tool
            elif state == 'customers':
                customer = Customer.create_from_line(line)
                problem['customers'].update({customer.id:customer})
            elif state == 'requests':
                request = Request.create_from_line(line)
                problem['requests'].update({request.id:request})
            #elif state == 'distance':
                #problem['distance'].append(Distance.create_from_line(line))

    createDistanceMatrix(problem)
    #print(problem)
    #pretty print via json.dumps
    print(json.dumps(problem, sort_keys=True, indent=4, default=str))

    #problem = Problem(problem['tools'], problem['customers'], problem['requests'])
    genetic_solver.solve_problem(problem)


def getValueFromLine(line):
    return line.split('=', 1)[1].strip()


def createDistanceMatrix(problem):
    lenCustomers = range(len(problem['customers']))
    problem['distance'] = [[0 for _ in lenCustomers] for _ in lenCustomers]
    for k1, v1 in problem['customers'].items():
        for k2, v2 in problem['customers'].items():
            problem['distance'][k1][k2] = distanceBetweenPoints(v1, v2)


def distanceBetweenPoints(p1, p2):
    diffX = math.fabs(p1.x - p2.x)
    diffY = math.fabs(p1.y - p2.y)
    return math.floor(math.sqrt(math.pow(diffX, 2) + math.pow(diffY, 2)))


if __name__ == '__main__':
    exit = main()
    sys.exit(exit)