from forest_management_system.components.health_status import HealthStatus

def simulate_infection(forest_graph, start_tree_id):
    # BFS
    infected = set()
    visited = set()
    bfs_list = []
    bfs_list.append(start_tree_id)
    while len(bfs_list) > 0:
        node = bfs_list[0]
        bfs_list = bfs_list[1:]
        if node in visited:
            continue
        visited.add(node)
        infected.add(node)
        neighbors = forest_graph.get_neighbors(node)
        for i in range(len(neighbors)):
            neighbor = neighbors[i]
            if neighbor not in visited and neighbor not in infected:
                if forest_graph.trees[neighbor].health_status != HealthStatus.INFECTED:
                    bfs_list.append(neighbor)
    return infected
