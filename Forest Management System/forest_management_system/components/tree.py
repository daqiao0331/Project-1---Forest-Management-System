from .health_status import HealthStatus

class Tree:
    def __init__(self, tree_id, species, age, health_status, forest=None):
        self.tree_id = tree_id
        self.species = species
        self.age = age
        self.forest = forest
        self.set_health_status(health_status)

    def set_health_status(self, status):
        if isinstance(status, HealthStatus):
            self._health_status = status
            return
        try:
            if isinstance(status, str):
                try:
                    self._health_status = HealthStatus[status.upper()]
                except KeyError:
                    self._health_status = HealthStatus(status.lower())
            else:
                self._health_status = HealthStatus(status)
        except (ValueError, TypeError, KeyError):
            raise ValueError(f"'{status}' is not a valid HealthStatus or cannot be converted.")

    @property
    def health_status(self):
        return self._health_status
    
    @health_status.setter
    def health_status(self, status):
        self.set_health_status(status)

    def __repr__(self):
        return (f"Tree(id={self.tree_id}, species={self.species}, age={self.age}, "
                f"health_status={self.health_status.name}, forest={self.forest})")

    def __eq__(self, other):
        if not isinstance(other, Tree):
            return False
        return self.tree_id == other.tree_id

    def __lt__(self, other):
        return self.tree_id < other.tree_id

# example usage:
# Tree(id=1, species=Oak, age=50, health_status=HEALTHY, forest=None)
# Tree(id=2, species=Pine, age=30, health_status=INFECTED, forest=None)
# Tree(id=3, species=Maple, age=40, health_status=AT_RISK, forest=None)
