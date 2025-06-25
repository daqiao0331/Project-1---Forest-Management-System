from forest_management_system.components.health_status import HealthStatus

def simulate_infection(forest_graph, start_tree_id):
    """
    Simulate infection spread from a given tree using BFS (graph structure, no deque)
    """
    infected = set()
    queue = [start_tree_id]
    while queue:
        current = queue.pop(0)
        if current in infected:
            continue
        infected.add(current)
        for neighbor in forest_graph.get_neighbors(current):
            if neighbor not in infected and forest_graph.trees[neighbor].health_status != HealthStatus.INFECTED:
                queue.append(neighbor)
    return infected
