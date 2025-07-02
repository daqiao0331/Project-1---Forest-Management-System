import heapq

def find_shortest_path(forest_graph, start_tree_id, end_tree_id):
    if start_tree_id not in forest_graph.trees or end_tree_id not in forest_graph.trees:
        return [], float('inf')
    
    if start_tree_id == end_tree_id:
        return [start_tree_id], 0
    
    # Initialize distances with infinity for all nodes except start
    dist = {tid: float('inf') for tid in forest_graph.trees}
    dist[start_tree_id] = 0
    
    # Keep track of previous node in path
    prev = {tid: None for tid in forest_graph.trees}
    
    # Priority queue with (distance, node_id)
    pq = [(0, start_tree_id)]
    visited = set()
    
    while pq:
        # Get the node with the smallest distance
        current_dist, current_id = heapq.heappop(pq)
        
        # If we've already processed this node, skip it
        if current_id in visited:
            continue
            
        # Mark as visited
        visited.add(current_id)
        
        # If we've reached the destination, we're done
        if current_id == end_tree_id:
            break
            
        # Check all neighbors of the current node
        for neighbor_id in forest_graph.get_neighbors(current_id):
            if neighbor_id in visited:
                continue   
            # Calculate distance through current node
            edge_weight = forest_graph.get_distance(current_id, neighbor_id)
            new_dist = dist[current_id] + edge_weight
            # If this path is shorter than what we currently have
            if new_dist < dist[neighbor_id]:
                dist[neighbor_id] = new_dist
                prev[neighbor_id] = current_id
                heapq.heappush(pq, (new_dist, neighbor_id))
    # Reconstruct the path
    path = []
    current = end_tree_id
    # Check if end is reachable
    if prev[current] is not None or current == start_tree_id:
        while current is not None:
            path.insert(0, current)
            current = prev[current]
        return path, dist[end_tree_id]
    else:
        return [], float('inf')
