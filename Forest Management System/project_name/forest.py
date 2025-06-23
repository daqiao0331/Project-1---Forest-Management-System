class Forest:
    def __init__(self, name, location, area):
        self.name = name
        self.location = location
        self.area = area
        self.trees = []

    def add_tree(self, tree):
        self.trees.append(tree)

    def remove_tree(self, tree):
        if tree in self.trees:
            self.trees.remove(tree)

    def get_tree_count(self):
        return len(self.trees)

    def __repr__(self):
        return f"Forest(name={self.name}, location={self.location}, area={self.area}, trees={len(self.trees)})"
