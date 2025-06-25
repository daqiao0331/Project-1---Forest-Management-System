from forest_management_system.components.health_status import HealthStatus
'''
DFS algorithm to find reserves in a forest graph
'''
def find_reserves(forest_graph):
    visited = set()
    reserves = []
    def dfs(current, reserve):
        if current in visited:
            return
        if forest_graph.trees[current].health_status != HealthStatus.HEALTHY:
            return
        visited.add(current)
        reserve.add(current)
        for neighbor in forest_graph.get_neighbors(current):
            if neighbor not in visited and forest_graph.trees[neighbor].health_status == HealthStatus.HEALTHY:
                dfs(neighbor, reserve)
    for tree_id, tree in forest_graph.trees.items():
        if tree.health_status == HealthStatus.HEALTHY and tree_id not in visited:
            reserve = set()
            dfs(tree_id, reserve)
            if reserve:
                reserves.append(reserve)
    return reserves
