def find_shortest_path(forest_graph, start_tree_id, end_tree_id):
    """
    Finds the shortest path between two trees using Dijkstra's algorithm.
    """
    dist = {tid: float('inf') for tid in forest_graph.trees}
    prev = {tid: None for tid in forest_graph.trees}
    dist[start_tree_id] = 0
    visited = set()
    n = len(forest_graph.trees)
    for _ in range(n):
        # Find the unvisited node with the smallest distance
        u = None
        min_dist = float('inf')
        for tid in forest_graph.trees:
            if tid not in visited and dist[tid] < min_dist:
                min_dist = dist[tid]
                u = tid
        if u is None:
            break  # The rest are unreachable
        visited.add(u)
        if u == end_tree_id:
            break
        # Update distances for all neighbors
        for path in forest_graph.paths:
            if path.tree1.tree_id == u:
                v = path.tree2.tree_id
            elif path.tree2.tree_id == u:
                v = path.tree1.tree_id
            else:
                continue
            if v in visited:
                continue
            alt = dist[u] + path.weight
            if alt < dist[v]:
                dist[v] = alt
                prev[v] = u
    # Reconstruct the path
    path = []
    u = end_tree_id
    if prev[u] is not None or u == start_tree_id:
        while u is not None:
            path.insert(0, u)
            u = prev[u]
    if path and path[0] == start_tree_id:
        return path, dist[end_tree_id]
    else:
        return [], float('inf')
