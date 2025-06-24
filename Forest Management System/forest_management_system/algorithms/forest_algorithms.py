from collections import deque
from components.health_status import HealthStatus

def find_reserves(forest_graph):
    """
    Find all clusters (connected components) of healthy trees in the forest graph.
    Returns a list of sets, each set contains the tree_ids of a reserve.
    """
    visited = set()
    reserves = []
    for tree_id, tree in forest_graph.trees.items():
        if tree.health_status == HealthStatus.HEALTHY and tree_id not in visited:
            # BFS/DFS to find all connected healthy trees
            stack = [tree_id]
            reserve = set()
            while stack:
                current = stack.pop()
                if current in visited:
                    continue
                if forest_graph.trees[current].health_status == HealthStatus.HEALTHY:
                    visited.add(current)
                    reserve.add(current)
                    # Add all healthy neighbors
                    for path in forest_graph.paths:
                        neighbor = None
                        if path.tree1.tree_id == current:
                            neighbor = path.tree2.tree_id
                        elif path.tree2.tree_id == current:
                            neighbor = path.tree1.tree_id
                        if neighbor and neighbor not in visited and forest_graph.trees[neighbor].health_status == HealthStatus.HEALTHY:
                            stack.append(neighbor)
            if reserve:
                reserves.append(reserve)
    return reserves

def simulate_infection(forest_graph, start_tree_id):
    """
    Simulate infection spread from a given tree using BFS.
    Returns a set of infected tree_ids (including the start).
    """
    infected = set()
    queue = deque([start_tree_id])
    while queue:
        current = queue.popleft()
        if current in infected:
            continue
        infected.add(current)
        for path in forest_graph.paths:
            neighbor = None
            if path.tree1.tree_id == current:
                neighbor = path.tree2.tree_id
            elif path.tree2.tree_id == current:
                neighbor = path.tree1.tree_id
            if neighbor and neighbor not in infected and forest_graph.trees[neighbor].health_status != HealthStatus.INFECTED:
                queue.append(neighbor)
    return infected

def find_shortest_path(forest_graph, start_tree_id, end_tree_id):
    """
    Find the shortest path between two trees using Dijkstra's algorithm.
    Returns (path_list, total_distance)
    """
    import heapq
    dist = {tid: float('inf') for tid in forest_graph.trees}
    prev = {tid: None for tid in forest_graph.trees}
    dist[start_tree_id] = 0
    heap = [(0, start_tree_id)]
    while heap:
        d, u = heapq.heappop(heap)
        if u == end_tree_id:
            break
        for path in forest_graph.paths:
            if path.tree1.tree_id == u:
                v = path.tree2.tree_id
            elif path.tree2.tree_id == u:
                v = path.tree1.tree_id
            else:
                continue
            alt = d + path.weight
            if alt < dist[v]:
                dist[v] = alt
                prev[v] = u
                heapq.heappush(heap, (alt, v))
    # reconstruct path
    path = []
    u = end_tree_id
    if prev[u] is not None or u == start_tree_id:
        while u is not None:
            path.insert(0, u)
            u = prev[u]
    return path, dist[end_tree_id] if path else ([], float('inf'))
