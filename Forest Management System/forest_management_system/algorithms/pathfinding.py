def find_shortest_path(forest_graph, start_tree_id, end_tree_id):
    """
    Dijkstra's algorithm with visited set.
    """
    import heapq
    dist = {tid: float('inf') for tid in forest_graph.trees}
    prev = {tid: None for tid in forest_graph.trees}
    dist[start_tree_id] = 0
    heap = [(0, start_tree_id)]
    visited = set()
    while heap:
        d, u = heapq.heappop(heap)
        if u in visited:
            continue
        visited.add(u)
        if u == end_tree_id:
            break
        for path in forest_graph.paths:
            if path.tree1.tree_id == u:
                v = path.tree2.tree_id
            elif path.tree2.tree_id == u:
                v = path.tree1.tree_id
            else:
                continue
            if v in visited:
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
    if path and path[0] == start_tree_id:
        return path, dist[end_tree_id]
    else:
        return [], float('inf')
