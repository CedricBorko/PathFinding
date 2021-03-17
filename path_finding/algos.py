import time
from queue import Queue

from path_finding.utils import PriorityQueue, Graph, heuristic


def bfs(graph, start, goal, diagonals, main_window):
    frontier = Queue()
    frontier.put(start)
    came_from = {}
    while not frontier.empty():
        c = frontier.get()
        if c == goal:
            break

        for n in graph.neighbors(c, diagonals):
            if n not in came_from:
                frontier.put(n)
                came_from[n] = c

    main_window.path_BFS = get_path(came_from, start, goal)
    main_window.visited_nodes = came_from
    main_window.update()


def aStar(graph: Graph, start, goal, diagonals, main_window, dijkstra=False):
    frontier = PriorityQueue()
    frontier.put(start, 0)
    came_from = {}
    cost_so_far = {start: 0}
    came_from[start] = None

    while not frontier.empty():
        c = frontier.get()
        if c == goal:
            break

        for n in graph.neighbors(c, diagonals):
            new_cost = cost_so_far[c] + graph.cost(c, n)
            if n not in cost_so_far or new_cost < cost_so_far[n]:
                cost_so_far[n] = new_cost
                priority = new_cost + (heuristic(n, goal) if not dijkstra else 1)
                frontier.put(n, priority)
                came_from[n] = c

    if dijkstra:
        main_window.path_DIJKSTRA = get_path(came_from, start, goal)
    else:
        main_window.path_ASTAR = get_path(came_from, start, goal)

    main_window.visited_nodes = came_from
    main_window.update()


def get_path(came_from, start, goal):
    """Retrieves the path by backtracking the parent nodes from goal to start."""
    current = goal
    path = []
    while current != start:
        path.append(current)
        try:
            current = came_from[current]
        except KeyError:
            return []
    path.append(start)
    return path
