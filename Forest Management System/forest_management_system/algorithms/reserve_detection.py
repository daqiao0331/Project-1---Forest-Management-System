from forest_management_system.components.health_status import HealthStatus
'''
DFS algorithm to find valid reserves in a forest graph.
A reserve is a connected component of 2 or more healthy trees,
and none of them are directly connected to any infected or at-risk tree.
'''
def find_reserves(forest_graph):
    reserves = []
    visited = set()

    def is_isolated_from_nonhealthy(group):
        # 检查group内所有树是否都没有与非健康树直接相连
        for tree_id in group:
            for neighbor in forest_graph.get_neighbors(tree_id):
                if forest_graph.trees[neighbor].health_status != HealthStatus.HEALTHY and neighbor not in group:
                    return False
        return True

    def dfs(tree_id, group):
        if tree_id in visited:
            return
        if forest_graph.trees[tree_id].health_status != HealthStatus.HEALTHY:
            return
        visited.add(tree_id)
        group.add(tree_id)
        for neighbor in forest_graph.get_neighbors(tree_id):
            if forest_graph.trees[neighbor].health_status == HealthStatus.HEALTHY:
                dfs(neighbor, group)

    for tree_id in forest_graph.trees:
        if forest_graph.trees[tree_id].health_status == HealthStatus.HEALTHY and tree_id not in visited:
            group = set()
            dfs(tree_id, group)
            if len(group) >= 2 and is_isolated_from_nonhealthy(group):
                reserves.append(group)
    return reserves
