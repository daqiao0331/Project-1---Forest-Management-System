import csv
from .tree import Tree
from .path import Path
from .forest_graph import ForestGraph
from .health_status import HealthStatus
from tkinter import messagebox

def load_forest_from_files(tree_file, path_file):
    graph = ForestGraph()
    duplicate_ids = []
    
    # Load trees
    with open(tree_file, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            tree_id = int(row['tree_id'])
            
            # Check if tree_id already exists in the graph
            if tree_id in graph.trees:
                duplicate_ids.append(tree_id)
            
            tree = Tree(
                tree_id,
                row['species'],
                int(row['age']),
                HealthStatus[row['health_status'].replace(' ', '_').upper()]
            )
            graph.add_tree(tree)
    
    # If duplicate IDs were found, show a warning message
    if duplicate_ids:
        warning_msg = f"Warning: Duplicate tree IDs found in the data: {', '.join(map(str, duplicate_ids))}.\n" \
                      f"Later entries have overwritten earlier ones."
        messagebox.showwarning("Duplicate Tree IDs", warning_msg)
    
    # Load paths
    with open(path_file, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            try:
                t1_id = int(row['tree_1'])
                t2_id = int(row['tree_2'])
                
                if t1_id not in graph.trees:
                    messagebox.showwarning("Invalid Path", f"Path references non-existent tree ID: {t1_id}")
                    continue
                    
                if t2_id not in graph.trees:
                    messagebox.showwarning("Invalid Path", f"Path references non-existent tree ID: {t2_id}")
                    continue
                    
                t1 = graph.trees[t1_id]
                t2 = graph.trees[t2_id]
                path = Path(t1, t2, float(row['distance']))
                graph.add_path(path)
            except Exception as e:
                messagebox.showwarning("Path Error", f"Error adding path: {str(e)}")
                
    return graph
