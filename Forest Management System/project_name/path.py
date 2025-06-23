from .tree import Tree

class Path:
    def __init__(self, tree1: Tree, tree2: Tree, weight: float):
        if not isinstance(tree1, Tree) or not isinstance(tree2, Tree):
            raise ValueError("Both ends of a path must be Tree instances.")
        self.tree1 = tree1
        self.tree2 = tree2
        self.weight = weight

    def __repr__(self):
        return f"Path({self.tree1.tree_id} <-> {self.tree2.tree_id}, distance={self.weight})"

    def __eq__(self, other):
        if not isinstance(other, Path):
            return False
        return ((self.tree1 == other.tree1 and self.tree2 == other.tree2) or
                (self.tree1 == other.tree2 and self.tree2 == other.tree1)) and self.weight == other.weight
