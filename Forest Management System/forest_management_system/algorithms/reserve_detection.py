from forest_management_system.components.health_status import HealthStatus
'''
DFS algorithm to find reserves in a forest graph
'''
def find_reserves(forest_graph):
    reserves = []  # 所有保护区
    visited = set()  # 已经看过的树

    def dfs(tree_id, group):
        if tree_id in visited:
            return
        if forest_graph.trees[tree_id].health_status != HealthStatus.HEALTHY:
            return
        visited.add(tree_id)
        group.add(tree_id)
        for neighbor in forest_graph.get_neighbors(tree_id):
            dfs(neighbor, group)

    for tree_id in forest_graph.trees:
        if forest_graph.trees[tree_id].health_status == HealthStatus.HEALTHY and tree_id not in visited:
            group = set()
            dfs(tree_id, group)
            if group:
                reserves.append(group)
    return reserves
