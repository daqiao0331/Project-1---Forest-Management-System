import csv
from .tree import Tree
from .path import Path
from .forest_graph import ForestGraph
from .health_status import HealthStatus

def load_forest_from_files(tree_file, path_file):
    graph = ForestGraph()
    # Load trees
    with open(tree_file, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            tree = Tree(
                int(row['tree_id']),
                row['species'],
                int(row['age']),
                HealthStatus[row['health_status'].replace(' ', '_').upper()]
            )
            graph.add_tree(tree)
    # Load paths
    with open(path_file, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            t1 = graph.trees[int(row['tree_1'])]
            t2 = graph.trees[int(row['tree_2'])]
            path = Path(t1, t2, float(row['distance']))
            graph.add_path(path)
    return graph
