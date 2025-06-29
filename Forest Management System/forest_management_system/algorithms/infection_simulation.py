import numpy as np
import heapq
from forest_management_system.data_structures.health_status import HealthStatus

def simulate_infection(forest_graph, start_tree_id):
    """
    Simulates infection spread using a priority queue instead of a regular queue.
    Trees closer to infected trees get infected first.
    
    Args:
        forest_graph: The forest graph
        start_tree_id: The ID of the starting tree
        
    Returns:
        List of tuples (tree_id, from_id, days_to_infect) in order of infection.
        days_to_infect represents the number of days it takes for a tree to become infected.
    """
    if start_tree_id not in forest_graph.trees:
        return []
        
    # Get the starting tree and ensure it's infected
    start_tree = forest_graph.trees[start_tree_id]
    if start_tree.health_status != HealthStatus.INFECTED:
        return []
    
    infected = set([start_tree_id])
    visited = set([start_tree_id])
    infection_order = [(start_tree_id, None, 0)]  # (tree_id, from_id, days_to_infect)
    
    # Priority queue with (days_to_infect, tree_id, from_id)
    # Using days as priority ensures trees get infected based on distance
    pq = []
    
    # Add neighbors of the starting tree to the queue
    for neighbor_id in forest_graph.get_neighbors(start_tree_id):
        if neighbor_id not in visited:
            # Days to infect is proportional to distance (1 unit = 1 day)
            distance = forest_graph.get_distance(start_tree_id, neighbor_id)
            days_to_infect = distance  # 1 distance unit = 1 day
            heapq.heappush(pq, (days_to_infect, neighbor_id, start_tree_id))
    
    while pq:
        days_to_infect, node, from_id = heapq.heappop(pq)
        
        if node in visited:
            continue
            
        visited.add(node)
        infected.add(node)
        infection_order.append((node, from_id, days_to_infect))
        
        # Only trees that are not already INFECTED can get infected
        if node in forest_graph.trees and forest_graph.trees[node].health_status != HealthStatus.INFECTED:
            for neighbor_id in forest_graph.get_neighbors(node):
                if neighbor_id not in visited:
                    distance = forest_graph.get_distance(node, neighbor_id)
                    # Cumulative days: current days + additional days based on distance
                    new_days = days_to_infect + distance
                    heapq.heappush(pq, (new_days, neighbor_id, node))
    
    return infection_order
