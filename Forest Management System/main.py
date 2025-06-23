from project_name.forest import Forest
from project_name.tree import Tree
from project_name.utils import find_trees_by_health, count_trees_by_species

def main():
    # 示例数据
    forest1 = Forest('Green Woods', 'North Zone', 1200)
    tree1 = Tree('Pine', 10, 'Healthy', forest1.name)
    tree2 = Tree('Oak', 5, 'Sick', forest1.name)
    tree3 = Tree('Birch', 7, 'Healthy', forest1.name)
    forest1.add_tree(tree1)
    forest1.add_tree(tree2)
    forest1.add_tree(tree3)

    print(forest1)
    print('所有树：', forest1.trees)
    print('健康的树：', find_trees_by_health(forest1.trees, 'Healthy'))
    print('树种统计：', count_trees_by_species(forest1.trees))

if __name__ == '__main__':
    main()
