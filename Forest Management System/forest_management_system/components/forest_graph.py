from .tree import Tree
from .path import Path

class ForestGraph:
    def __init__(self):
        self.trees = {}
        self.paths = []

    def add_tree(self, tree: Tree):
        self.trees[tree.tree_id] = tree

    def remove_tree(self, tree_id):
        if tree_id in self.trees:
            self.trees.pop(tree_id)
            self.paths = [p for p in self.paths if p.tree1.tree_id != tree_id and p.tree2.tree_id != tree_id]

    def add_path(self, path: Path):
        if path not in self.paths:
            self.paths.append(path)

    def remove_path(self, tree_id1, tree_id2):
        self.paths = [p for p in self.paths if not ((p.tree1.tree_id == tree_id1 and p.tree2.tree_id == tree_id2) or (p.tree1.tree_id == tree_id2 and p.tree2.tree_id == tree_id1))]

    def update_distance(self, tree_id1, tree_id2, new_weight):
        for p in self.paths:
            if (p.tree1.tree_id == tree_id1 and p.tree2.tree_id == tree_id2) or (p.tree1.tree_id == tree_id2 and p.tree2.tree_id == tree_id1):
                p.weight = new_weight

    def update_health_status(self, tree_id, new_status):
        if tree_id in self.trees:
            self.trees[tree_id].set_health_status(new_status)

    def get_neighbors(self, tree_id):
        neighbors = []
        for path in self.paths:
            if path.tree1.tree_id == tree_id:
                neighbors.append(path.tree2.tree_id)
            elif path.tree2.tree_id == tree_id:
                neighbors.append(path.tree1.tree_id)
        return neighbors

    def __repr__(self):
        s = 'ForestGraph:\n'
        for t in self.trees.values():
            s += f'  {t}\n'
        s += 'Paths:\n'
        for p in self.paths:
            s += f'  {p}\n'
        return s

    def clear(self):
        self.trees.clear()
        self.paths.clear()
