"""
Utility functions for forest management.
"""
from collections import Counter
from ..data_structures.health_status import HealthStatus

def find_trees_by_health(trees, health_status):
    """
    Find all trees with the specified health status.
    
    Args:
        trees: List of Tree objects
        health_status: HealthStatus enum value
        
    Returns:
        List of Tree objects with the specified health status
    """
    return [tree for tree in trees if tree.health_status == health_status]

def count_trees_by_species(trees):
    """
    Count the number of trees for each species.
    
    Args:
        trees: List of Tree objects
        
    Returns:
        Dictionary with species as keys and counts as values
    """
    return Counter(tree.species for tree in trees) 