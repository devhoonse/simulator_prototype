
from typing import Dict, List
from collections import defaultdict


# queue: list = []


def bfs_test():
    graph: Dict[str, List[str]] = {
        'A': ['B'],
        'B': ['C', 'D'],
        'C': ['G'],
        'D': ['E'],
        'E': ['F'],
        'F': ['G'],
        'G': ['H'],
        'H': []
    }

    visited: list = []
    queue: list = []

    def bfs(visited, graph, node):
        visited.append(node)
        queue.append(node)

        while queue:
            s = queue.pop(0)
            print(s, end=" ")

            for neighbour in graph[s]:
                if neighbour not in visited:
                    visited.append(neighbour)
                    queue.append(neighbour)

    # Driver Code
    bfs(visited, graph, 'A')


if __name__ == '__main__':
    bfs_test()
