import heapq
import math
from typing import Tuple

Location = Tuple[int, int]


class Graph:
    """A Object that holds locations in 2D space."""

    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.walls = []
        self.diagonal_cost = 14
        self.straight_cost = 10

    def in_bounds(self, pos):
        """:returns if a given position is within the graphs boundaries"""
        x, y = pos
        return 0 <= x < self.width and 0 <= y < self.height

    def no_obstacle(self, pos):
        return pos not in self.walls

    def neighbors(self, pos, diagonals=False):
        """Calculates the neighbors for each Node in the Graph."""
        x, y = pos
        neighbors = [(x + 1, y), (x - 1, y), (x, y - 1), (x, y + 1)]
        if diagonals:
            neighbors += [(x + 1, y + 1), (x - 1, y + 1), (x + 1, y - 1), (x - 1, y - 1)]
        if (x + y) % 2 == 0: neighbors.reverse()
        results = filter(self.in_bounds, neighbors)
        results = filter(self.no_obstacle, results)
        return results

    @staticmethod
    def cost(from_id, to_id):
        return distance(from_id, to_id) * 10


class PriorityQueue:
    def __init__(self):
        self.elements = []

    def empty(self):
        return not self.elements

    def put(self, item, priority):
        heapq.heappush(self.elements, (priority, item))

    def get(self):
        return heapq.heappop(self.elements)[1]


def heuristic(a, b, bias=10):
    x1, y1 = a
    x2, y2 = b
    return (math.fabs(x1 - x2) + math.fabs(y1 - y2)) * bias


def distance(a, b):
    x1, y1 = a
    x2, y2 = b
    return math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)
