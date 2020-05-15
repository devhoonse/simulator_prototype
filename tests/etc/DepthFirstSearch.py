
from typing import List


graph: dict = {
    'A': {'B'},
    'B': {'C', 'D'},
    'C': {'G'},
    'D': {'E'},
    'E': {'F'},
    'F': {'G'},
    'G': {'H'},
    'H': {}
}


def dfs_recursive(graph, root, visited=None):
    if visited is None:
        visited = set()

    print(root)
    visited.add(root)

    # 주어진 root 과 연결되어 있는 다른 node 들에 대해 방문하지 않은 것들만 재귀 호출합니다.
    for node in graph[root] - visited:
        dfs_recursive(graph, node, visited)

    return visited


if __name__ == '__main__':
    paths_list = dfs_recursive(graph, 'A')

    print("Debugging Point")
