from collections import deque
from .health_status import HealthStatus

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
