import pytest
import numpy as np
from forest_management_system.algorithms.force_layout import force_directed_layout

def test_force_directed_layout_basic():
    # Simple graph: 3 nodes in a line
    trees = [1, 2, 3]
    adj_list = {
        1: {2: 1},
        2: {1: 1, 3: 1},
        3: {2: 1}
    }
    weights = {
        (1, 2): 1,
        (2, 1): 1,
        (2, 3): 1,
        (3, 2): 1
    }
    positions = force_directed_layout(trees, adj_list, weights, canvas_size=(100, 100), iterations=100, min_distance=10)
    assert isinstance(positions, dict)
    assert set(positions.keys()) == set(trees)
    for pos in positions.values():
        assert 0 <= pos[0] <= 100
        assert 0 <= pos[1] <= 100
    # Check minimum distance
    coords = list(positions.values())
    for i in range(len(coords)):
        for j in range(i+1, len(coords)):
            dist = np.sqrt((coords[i][0] - coords[j][0])**2 + (coords[i][1] - coords[j][1])**2)
            assert dist >= 9  # Allow small numerical error

def test_force_directed_layout_isolated():
    # Graph with isolated node
    trees = [1, 2, 3, 4]
    adj_list = {
        1: {2: 1},
        2: {1: 1},
        3: {},
        4: {}
    }
    weights = {
        (1, 2): 1,
        (2, 1): 1
    }
    positions = force_directed_layout(trees, adj_list, weights, canvas_size=(100, 100), iterations=100, min_distance=10)
    assert 3 in positions and 4 in positions
    # Isolated nodes should be within canvas
    for tid in [3, 4]:
        x, y = positions[tid]
        assert 0 <= x <= 100
        assert 0 <= y <= 100

def test_force_directed_layout_deterministic():
    # With fixed random seed, output should be deterministic
    import random
    random.seed(42)
    np.random.seed(42)
    trees = [1, 2]
    adj_list = {1: {2: 1}, 2: {1: 1}}
    weights = {(1, 2): 1, (2, 1): 1}
    pos1 = force_directed_layout(trees, adj_list, weights, canvas_size=(100, 100), iterations=50, min_distance=5)
    random.seed(42)
    np.random.seed(42)
    pos2 = force_directed_layout(trees, adj_list, weights, canvas_size=(100, 100), iterations=50, min_distance=5)
    assert pos1 == pos2 