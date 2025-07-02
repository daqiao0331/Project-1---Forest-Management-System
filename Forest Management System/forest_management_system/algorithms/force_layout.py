import random
import numpy as np
from collections import defaultdict

def force_directed_layout(trees, adj_list, weights, canvas_size=(100, 100), iterations=400, min_distance=20):
    """
    Compute node positions using a force-directed layout algorithm.

    Args:
        trees: List of node IDs.
        adj_list: Dict mapping node ID to dict of neighbor ID -> weight.
        weights: Dict mapping (node1, node2) tuple to edge weight.
        canvas_size: Tuple (width, height) for layout area.
        iterations: Number of simulation steps.
        min_distance: Minimum allowed distance between nodes.

    Returns:
        Dict mapping node ID to (x, y) position.
    """
    width, height = canvas_size
    n_trees = len(trees)
    if n_trees == 0:
        return {}

    # Initial random positions
    positions = {}
    for tree_id in trees:
        positions[tree_id] = (
            random.uniform(0.1 * width, 0.9 * width),
            random.uniform(0.1 * height, 0.9 * height)
        )

    # Normalize weights
    if weights:
        weight_values = list(weights.values())
        min_weight = min(weight_values)
        max_weight = max(weight_values)
        weight_range = max(max_weight - min_weight, 1)
        target_min, target_max = 0.15 * width, 0.7 * width
        for key, weight in list(weights.items()):
            normalized = target_min + (weight - min_weight) * (target_max - target_min) / weight_range
            weights[key] = normalized

    # Build neighbors
    neighbors = defaultdict(list)
    for tid1, tid2 in weights:
        neighbors[tid1].append(tid2)
        neighbors[tid2].append(tid1)

    temperature = 1.0 * max(width, height)
    for iteration in range(iterations):
        temperature *= 0.98
        forces = {tid: [0, 0] for tid in trees}

        # Spring forces
        for tid1, tid2 in weights:
            x1, y1 = positions[tid1]
            x2, y2 = positions[tid2]
            dx, dy = x2 - x1, y2 - y1
            distance = max(np.sqrt(dx*dx + dy*dy), 0.01)
            ideal_distance = weights[(tid1, tid2)]
            force_factor = (distance - ideal_distance) / distance
            fx, fy = force_factor * dx, force_factor * dy
            forces[tid1][0] += fx
            forces[tid1][1] += fy
            forces[tid2][0] -= fx
            forces[tid2][1] -= fy

        # Repulsion forces
        for i, tid1 in enumerate(trees):
            for tid2 in trees[i+1:]:
                x1, y1 = positions[tid1]
                x2, y2 = positions[tid2]
                dx, dy = x2 - x1, y2 - y1
                distance = max(np.sqrt(dx*dx + dy*dy), 0.01)
                force_factor = 2.0 * max(width, height) / (distance * distance)
                fx, fy = force_factor * dx / distance, force_factor * dy / distance
                forces[tid1][0] -= fx
                forces[tid1][1] -= fy
                forces[tid2][0] += fx
                forces[tid2][1] += fy

        # Boundary forces
        for tid in trees:
            x, y = positions[tid]
            if x < 0.05 * width:
                forces[tid][0] += (0.05 * width - x) * 0.5
            elif x > 0.95 * width:
                forces[tid][0] -= (x - 0.95 * width) * 0.5
            if y < 0.05 * height:
                forces[tid][1] += (0.05 * height - y) * 0.5
            elif y > 0.95 * height:
                forces[tid][1] -= (y - 0.95 * height) * 0.5

        # Isolated nodes
        isolated = [tid for tid in trees if not neighbors[tid]]
        if isolated:
            corners = [
                (0.15 * width, 0.15 * height), (0.85 * width, 0.15 * height),
                (0.15 * width, 0.85 * height), (0.85 * width, 0.85 * height)
            ]
            sides = [
                (0.5 * width, 0.15 * height), (0.85 * width, 0.5 * height),
                (0.5 * width, 0.85 * height), (0.15 * width, 0.5 * height)
            ]
            positions_list = corners + sides
            for i, tid in enumerate(isolated):
                if i < len(positions_list):
                    positions[tid] = positions_list[i]
                else:
                    positions[tid] = (
                        random.uniform(0.1 * width, 0.9 * width),
                        random.uniform(0.1 * height, 0.9 * height)
                    )

        # Limit movement
        for tid in trees:
            fx, fy = forces[tid]
            force_mag = np.sqrt(fx*fx + fy*fy)
            if force_mag > temperature:
                fx = fx * temperature / force_mag
                fy = fy * temperature / force_mag
            x, y = positions[tid]
            new_x = max(0.05 * width, min(0.95 * width, x + fx))
            new_y = max(0.05 * height, min(0.95 * height, y + fy))
            positions[tid] = (new_x, new_y)

    # Final adjustment for minimum distance
    for _ in range(50):
        has_overlap = False
        for i, tid1 in enumerate(trees):
            for tid2 in trees[i+1:]:
                x1, y1 = positions[tid1]
                x2, y2 = positions[tid2]
                dist = np.sqrt((x2-x1)**2 + (y2-y1)**2)
                if dist < min_distance:
                    has_overlap = True
                    angle = np.arctan2(y2 - y1, x2 - x1)
                    push_dist = (min_distance - dist) / 2
                    positions[tid1] = (
                        max(0.05 * width, min(0.95 * width, x1 - push_dist * np.cos(angle))),
                        max(0.05 * height, min(0.95 * height, y1 - push_dist * np.sin(angle)))
                    )
                    positions[tid2] = (
                        max(0.05 * width, min(0.95 * width, x2 + push_dist * np.cos(angle))),
                        max(0.05 * height, min(0.95 * height, y2 + push_dist * np.sin(angle)))
                    )
        if not has_overlap:
            break

    return positions 