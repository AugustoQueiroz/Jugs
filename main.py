import time
from graphviz import Digraph
import argparse

parser = argparse.ArgumentParser(
    description='''This is a solver for the general version of the 3 jugs problem.\n
    The problem goes like this: You are given three jugs that can carry up to 8L, 5L, and 3L respectively. Initially the first jug is full (i.e. has 8L in it) and the others are empty. Can you divide the 8L into two jugs, with 4L each, only by pouring from one jug into the other?\n
    The jugs' shapes are odd, such that you cannot "eyeball" it, when pouring from one jug into another you must do so either until the first is empty, or the second is full.\n\n

    In this generalized version you can change the limits of the jugs, or even how many there are, as well as the initial distribution and the desired distribution.
    '''
    )
parser.add_argument('-s', '--sizes', nargs='+', type=int, dest='sizes', required=True, help='The size limits for each jugs')
parser.add_argument('-i', '--initial_distribution', nargs='+', type=int, dest='distribution', required=True, help='The initial distribution')
parser.add_argument('-g', '--goal', nargs='+', type=int, dest='goal', help='The desired distribution to reach')

parser.add_argument('-v', '--visualize_graph', action='store_true', dest='make_vis', help='Create a visualization of the entire graph of possibilities')

class Configuration:
    def __init__(self, distribution, limits):
        self.distribution = distribution
        self.limits = limits
    
    def __str__(self):
        return ''.join(str(x) for x in self.distribution)
    
    def __hash__(self):
        return self.__str__().__hash__()
    
    def __eq__(self, other):
        return self.__hash__() == other.__hash__()
    
    def valid_next_configurations(self):
        result = set()

        new_distribution = self.distribution
        for i, content_1 in enumerate(self.distribution):
            if content_1 == 0:
                continue # There is nothing here to pass to another jug
            for j, content_2 in enumerate(self.distribution):
                # Pour from 1 into 2
                if content_2 < self.limits[j]:
                    # Can pour into 2
                    # Either all of one (content_2 + content_1)
                    # Or until it is filled
                    new_distribution[j] = min(self.limits[j], content_2 + content_1)
                    new_distribution[i] = content_1 - (new_distribution[j] - content_2)
                    if sum(new_distribution) == 8:
                        result.add(Configuration(new_distribution[:], self.limits))
                    new_distribution[i] = content_1
                    new_distribution[j] = content_2
        
        return result

def search(graph, start_node, end_node):
    candidate_paths = []
    curr_path = [start_node]
    while curr_path[-1] != end_node:
        for neighbour in graph[curr_path[-1]]:
            candidate_paths.append(curr_path + [neighbour])
        curr_path = candidate_paths.pop(0)
    
    return curr_path

def create_graphviz(graph):
    dot = Digraph()
    for vertex in graph:
        dot.node(str(vertex))
    
    for vertex in graph:
        for neighbour in graph[vertex]:
            dot.edge(str(vertex), str(neighbour))
    
    dot.render('test.gv')

if __name__ == '__main__':
    args = parser.parse_args()

    graph = {}
    c = Configuration(args.distribution, args.sizes)
    graph[c] = c.valid_next_configurations()

    frontier = graph[c]
    visited = {c}
    while len(frontier) > 0:
        current = frontier.pop()
        graph[current] = current.valid_next_configurations()
        visited.add(current)
        frontier = frontier.union(graph[current]) - visited

    if args.make_vis:
        create_graphviz(graph)
    
    if args.goal is not None:
        goal = Configuration(args.goal, args.sizes)
        print(f'Shortest solution for getting from {str(c)} to {str(goal)}')
        solution = search(graph, c, goal)
        for node in solution[:-1]:
            print(f'{node}->', end='')
        print(f'{solution[-1]}')