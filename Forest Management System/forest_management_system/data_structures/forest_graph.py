from .tree import Tree
from .path import Path

class ForestGraph:
    def __init__(self):
        self.trees = {}  # {tree_id: Tree object}
        self.adj_list = {}  # {tree_id: {neighbor_id: weight}}

    def add_tree(self, tree: Tree):
        self.trees[tree.tree_id] = tree
        if tree.tree_id not in self.adj_list:
            self.adj_list[tree.tree_id] = {}

    def remove_tree(self, tree_id):
        if tree_id in self.trees:
            self.trees.pop(tree_id)
            
            # Remove from adjacency list
            self.adj_list.pop(tree_id, None)
            
            # Remove all connections to this tree
            for tid in self.adj_list:
                if tree_id in self.adj_list[tid]:
                    self.adj_list[tid].pop(tree_id)

    def add_path(self, path: Path):
        tree1_id = path.tree1.tree_id
        tree2_id = path.tree2.tree_id
        weight = path.weight
        
        # Initialize adjacency list entries if they don't exist
        if tree1_id not in self.adj_list:
            self.adj_list[tree1_id] = {}
        if tree2_id not in self.adj_list:
            self.adj_list[tree2_id] = {}
        
        # Add to adjacency list (undirected graph)
        self.adj_list[tree1_id][tree2_id] = weight
        self.adj_list[tree2_id][tree1_id] = weight

    def remove_path(self, tree_id1, tree_id2):
        # Remove from adjacency list
        if tree_id1 in self.adj_list and tree_id2 in self.adj_list[tree_id1]:
            self.adj_list[tree_id1].pop(tree_id2)
        if tree_id2 in self.adj_list and tree_id1 in self.adj_list[tree_id2]:
            self.adj_list[tree_id2].pop(tree_id1)

    def update_distance(self, tree_id1, tree_id2, new_weight):
        # Update in adjacency list
        if tree_id1 in self.adj_list and tree_id2 in self.adj_list[tree_id1]:
            self.adj_list[tree_id1][tree_id2] = new_weight
        if tree_id2 in self.adj_list and tree_id1 in self.adj_list[tree_id2]:
            self.adj_list[tree_id2][tree_id1] = new_weight

    def update_health_status(self, tree_id, new_status):
        if tree_id in self.trees:
            self.trees[tree_id].set_health_status(new_status)

    def get_neighbors(self, tree_id):
        """Return a list of neighbor tree IDs with O(1) complexity."""
        if tree_id in self.adj_list:
            return list(self.adj_list[tree_id].keys())
        return []
    
    def get_distance(self, tree_id1, tree_id2):
        """Get the weight/distance between two trees with O(1) complexity."""
        if tree_id1 in self.adj_list and tree_id2 in self.adj_list[tree_id1]:
            return self.adj_list[tree_id1][tree_id2]
        return float('inf')  # If there's no direct edge

    def clear(self):
        """Remove all trees and paths from the forest graph."""
        self.trees.clear()
        self.adj_list.clear()

    def __repr__(self):
        s = 'ForestGraph:\n'
        for t in self.trees.values():
            s += f'  {t}\n'
        s += 'Adjacency List:\n'
        for tid, neighbors in self.adj_list.items():
            s += f'  {tid}: {neighbors}\n'
        return s
