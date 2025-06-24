from .health_status import HealthStatus

def find_reserves(forest_graph):
    """
    Find all clusters (connected components) of healthy trees in the forest graph.
    Returns a list of sets, each set contains the tree_ids of a reserve.
    """
    visited = set()
    reserves = []
    for tree_id, tree in forest_graph.trees.items():
        if tree.health_status == HealthStatus.HEALTHY and tree_id not in visited:
            stack = [tree_id]
            reserve = set()
            while stack:
                current = stack.pop()
                if current in visited:
                    continue
                if forest_graph.trees[current].health_status == HealthStatus.HEALTHY:
                    visited.add(current)
                    reserve.add(current)
                    for path in forest_graph.paths:
                        neighbor = None
                        if path.tree1.tree_id == current:
                            neighbor = path.tree2.tree_id
                        elif path.tree2.tree_id == current:
                            neighbor = path.tree1.tree_id
                        if neighbor and neighbor not in visited and forest_graph.trees[neighbor].health_status == HealthStatus.HEALTHY:
                            stack.append(neighbor)
            if reserve:
                reserves.append(reserve)
    return reserves
