import numpy as np
from forest_management_system.components.health_status import HealthStatus

def simulate_infection(forest_graph, start_tree_id):
    # BFS infection spread, returns the order of infection.
    infected = set()
    visited = set()
    infection_order = []  # (tree_id, from_id)
    queue = [(start_tree_id, None)]
    
    while queue:
        node, from_id = queue.pop(0)
        if node in visited:
            continue
        visited.add(node)
        infected.add(node)
        infection_order.append((node, from_id))
        
        neighbors = forest_graph.get_neighbors(node)
        
        # Calculate distances to neighbors and sort them.
        neighbor_distances = []
        for neighbor_id in neighbors:
            distance = float('inf')
            for path in forest_graph.paths:
                if (path.tree1.tree_id == node and path.tree2.tree_id == neighbor_id) or \
                   (path.tree1.tree_id == neighbor_id and path.tree2.tree_id == node):
                    distance = path.weight
                    break
            neighbor_distances.append((neighbor_id, distance))
            
        neighbor_distances.sort(key=lambda x: x[1])
        
        # Add sorted neighbors to the queue.
        for neighbor_id, _ in neighbor_distances:
            if neighbor_id not in visited and neighbor_id not in infected:
                if forest_graph.trees[neighbor_id].health_status != HealthStatus.INFECTED:
                    queue.append((neighbor_id, node))
    return infection_order
