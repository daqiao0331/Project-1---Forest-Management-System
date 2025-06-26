from forest_management_system.components.health_status import HealthStatus
'''
DFS algorithm to find reserves in a forest graph
'''
def find_reserves(forest_graph):
    reserves = []  # 存放所有保护区
    visited = set()  # 记录已经访问过的树

    def dfs(tree_id, reserve):
        # 如果已经访问过，直接返回
        if tree_id in visited:
            return
        # 只处理健康的树
        if forest_graph.trees[tree_id].health_status != HealthStatus.HEALTHY:
            return
        visited.add(tree_id)
        reserve.add(tree_id)
        # 遍历所有邻居
        for neighbor in forest_graph.get_neighbors(tree_id):
            dfs(neighbor, reserve)

    # 遍历所有树，找到每个健康且未访问的树，作为新保护区的起点
    for tree_id in forest_graph.trees:
        if forest_graph.trees[tree_id].health_status == HealthStatus.HEALTHY and tree_id not in visited:
            reserve = set()
            dfs(tree_id, reserve)
            if reserve:
                reserves.append(reserve)
    return reserves
