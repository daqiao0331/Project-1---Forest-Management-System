from components.health_status import HealthStatus

def simulate_infection(forest_graph, start_tree_id):
    """
    Simulate infection spread from a given tree using DFS on the graph structure.
    Returns a set of infected tree_ids (including the start).
    """
    infected = set()
    def dfs(current):
        if current in infected:
            return
        infected.add(current)
        for neighbor in forest_graph.get_neighbors(current):
            if neighbor not in infected and forest_graph.trees[neighbor].health_status != HealthStatus.INFECTED:
                dfs(neighbor)
    dfs(start_tree_id)
    return infected
