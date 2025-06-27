from forest_management_system.components.health_status import HealthStatus
'''
Find reserves: only groups of 3 or more healthy trees that form a complete (fully connected) subgraph (clique),
and none of them are directly connected to any infected or at-risk tree.
'''
def find_reserves(forest_graph):
    reserves = []
    visited = set()

    def dfs(tree_id, group):
        visited.add(tree_id)
        group.add(tree_id)
        for neighbor in forest_graph.get_neighbors(tree_id):
            if neighbor not in visited and forest_graph.trees[neighbor].health_status == HealthStatus.HEALTHY:
                dfs(neighbor, group)

    for tree_id in forest_graph.trees:
        if tree_id not in visited and forest_graph.trees[tree_id].health_status == HealthStatus.HEALTHY:
            group = set()
            dfs(tree_id, group)
            if len(group) >= 3:
                # check if the group is a clique
                is_clique = True
                group_list = list(group)
                for i in range(len(group_list)):
                    for j in range(i+1, len(group_list)):
                        t1, t2 = group_list[i], group_list[j]
                        if t2 not in forest_graph.get_neighbors(t1):
                            is_clique = False
                            break
                    if not is_clique:
                        break
                if not is_clique:
                    continue
                # Check if the group is isolated from infected trees
                isolated = True
                for tid in group:
                    for neighbor in forest_graph.get_neighbors(tid):
                        if neighbor not in group and forest_graph.trees[neighbor].health_status != HealthStatus.HEALTHY:
                            isolated = False
                            break
                    if not isolated:
                        break
                if isolated:
                    reserves.append(group)
    return reserves
