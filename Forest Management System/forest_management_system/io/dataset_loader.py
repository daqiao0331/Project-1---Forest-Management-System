import csv
import tkinter as tk
from tkinter import messagebox
from ..data_structures.tree import Tree
from ..data_structures.path import Path
from ..data_structures.forest_graph import ForestGraph
from ..data_structures.health_status import HealthStatus

def load_forest_from_files(tree_file, path_file):
    """
    Load forest data from CSV files with enhanced error handling.
    
    Args:
        tree_file: Path to trees CSV file
        path_file: Path to paths CSV file
        
    Returns:
        ForestGraph object containing the loaded data
        
    Raises:
        ValueError: If required columns are missing or there are format issues
        FileNotFoundError: If files don't exist
    """
    graph = ForestGraph()
    duplicate_ids = []
    errors = []
    tree_count = 0
    path_count = 0
    
    try:
        # Load trees
        with open(tree_file, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            
            # Validate columns
            required_columns = ['tree_id', 'species', 'age', 'health_status']
            if not all(col in reader.fieldnames for col in required_columns):
                missing = [col for col in required_columns if col not in reader.fieldnames]
                raise ValueError(f"Missing required columns in tree file: {', '.join(missing)}")
            
            for row_num, row in enumerate(reader, 2):  # Start at line 2 (after header)
                try:
                    tree_id = int(row['tree_id'])
                    
                    # Check if tree_id already exists in the graph
                    if tree_id in graph.trees:
                        duplicate_ids.append((tree_id, row_num))
                        continue
                    
                    # Create tree
                    tree = Tree(
                        tree_id,
                        row['species'],
                        int(row['age']),
                        HealthStatus[row['health_status'].replace(' ', '_').upper()]
                    )
                    graph.add_tree(tree)
                    tree_count += 1
                except ValueError as e:
                    errors.append(f"Line {row_num}: Invalid tree data - {str(e)}")
                except KeyError as e:
                    errors.append(f"Line {row_num}: Invalid health status '{row.get('health_status', '')}', must be HEALTHY, INFECTED or AT_RISK")
    except FileNotFoundError:
        raise FileNotFoundError(f"Tree file not found: {tree_file}")
    except Exception as e:
        raise ValueError(f"Error reading tree file: {str(e)}")
    
    # If no trees were loaded successfully, stop
    if tree_count == 0:
        error_msg = "No valid trees found in the data file."
        if errors:
            error_msg += f"\nErrors: {'; '.join(errors[:5])}"
            if len(errors) > 5:
                error_msg += f" and {len(errors) - 5} more."
        messagebox.showerror("Data Loading Error", error_msg)
        return graph
    
    # Show warnings about duplicate IDs
    if duplicate_ids:
        dup_details = ", ".join([f"ID {id} (line {line})" for id, line in duplicate_ids[:5]])
        if len(duplicate_ids) > 5:
            dup_details += f" and {len(duplicate_ids) - 5} more"
            
        warning_msg = f"Warning: {len(duplicate_ids)} duplicate tree IDs found in the data: {dup_details}.\n" \
                      f"Duplicate IDs were skipped."
        messagebox.showwarning("Duplicate Tree IDs", warning_msg)
    
    # Show general errors
    if errors:
        error_details = "\n".join(errors[:5])
        if len(errors) > 5:
            error_details += f"\n... and {len(errors) - 5} more errors."
        messagebox.showwarning("Data Loading Issues", f"Some data could not be loaded:\n{error_details}")
    
    # Load paths
    path_errors = []
    try:
        with open(path_file, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            
            # Validate columns - support both naming conventions
            tree1_col = 'tree_1' if 'tree_1' in reader.fieldnames else 'tree_id1'
            tree2_col = 'tree_2' if 'tree_2' in reader.fieldnames else 'tree_id2'
            distance_col = 'distance'
            
            if not (tree1_col in reader.fieldnames and tree2_col in reader.fieldnames and distance_col in reader.fieldnames):
                missing = []
                if tree1_col not in reader.fieldnames:
                    missing.append('tree_1/tree_id1')
                if tree2_col not in reader.fieldnames:
                    missing.append('tree_2/tree_id2')
                if distance_col not in reader.fieldnames:
                    missing.append('distance')
                raise ValueError(f"Missing required columns in path file: {', '.join(missing)}")
            
            for row_num, row in enumerate(reader, 2):
                try:
                    t1_id = int(row[tree1_col])
                    t2_id = int(row[tree2_col])
                    
                    if t1_id == t2_id:
                        path_errors.append(f"Line {row_num}: Self-loop path from {t1_id} to itself is not allowed")
                        continue
                        
                    if t1_id not in graph.trees:
                        path_errors.append(f"Line {row_num}: Path references non-existent tree ID: {t1_id}")
                        continue
                        
                    if t2_id not in graph.trees:
                        path_errors.append(f"Line {row_num}: Path references non-existent tree ID: {t2_id}")
                        continue
                        
                    t1 = graph.trees[t1_id]
                    t2 = graph.trees[t2_id]
                    
                    weight = float(row[distance_col])
                    if weight <= 0:
                        path_errors.append(f"Line {row_num}: Invalid distance: {weight} (must be positive)")
                        continue
                        
                    path = Path(t1, t2, weight)
                    graph.add_path(path)
                    path_count += 1
                except ValueError as e:
                    path_errors.append(f"Line {row_num}: Invalid path data - {str(e)}")
    except FileNotFoundError:
        messagebox.showwarning("Path File Error", f"Path file not found: {path_file}")
    except Exception as e:
        messagebox.showwarning("Path Loading Error", f"Error reading path file: {str(e)}")
    
    if path_errors:
        error_details = "\n".join(path_errors[:5])
        if len(path_errors) > 5:
            error_details += f"\n... and {len(path_errors) - 5} more errors."
        messagebox.showwarning("Path Loading Issues", f"Some paths could not be loaded:\n{error_details}")
    
    # Show summary
    messagebox.showinfo("Data Loading Summary", 
                       f"Successfully loaded:\n"
                       f"• {tree_count} trees\n"
                       f"• {path_count} paths\n\n"
                       f"Issues:\n"
                       f"• {len(duplicate_ids)} duplicate tree IDs\n"
                       f"• {len(errors)} tree data errors\n"
                       f"• {len(path_errors)} path data errors")
                
    return graph
