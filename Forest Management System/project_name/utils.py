def find_trees_by_health(trees, health_status):
    return [tree for tree in trees if tree.health == health_status]

def count_trees_by_species(trees):
    species_count = {}
    for tree in trees:
        species_count[tree.species] = species_count.get(tree.species, 0) + 1
    return species_count
