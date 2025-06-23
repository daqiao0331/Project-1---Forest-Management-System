class Tree:
    def __init__(self, species, age, health, forest=None):
        self.species = species
        self.age = age
        self.health = health
        self.forest = forest

    def __repr__(self):
        return f"Tree(species={self.species}, age={self.age}, health={self.health}, forest={self.forest})"
