from .health_status import HealthStatus

class Tree:
    def __init__(self, tree_id, species, age, health_status, forest=None):
        self.tree_id = tree_id
        self.species = species
        self.age = age
        self.forest = forest
        self.health_status = None
        self.set_health_status(health_status)

    def set_health_status(self, status):
        from .health_status import HealthStatus
        if not isinstance(status, HealthStatus):
            try:
                status = HealthStatus(status)
            except Exception:
                raise ValueError("health_status must be an instance of HealthStatus Enum")
        self.health_status = status

    def __repr__(self):
        return (f"Tree(id={self.tree_id}, species={self.species}, age={self.age}, "
                f"health_status={self.health_status.name}, forest={self.forest})")

    def __eq__(self, other):
        if not isinstance(other, Tree):
            return False
        return self.tree_id == other.tree_id

    def __lt__(self, other):
        return self.tree_id < other.tree_id

# 示例：三棵树数据
# Tree(id=1, species=Oak, age=50, health_status=HEALTHY, forest=None)
# Tree(id=2, species=Pine, age=30, health_status=INFECTED, forest=None)
# Tree(id=3, species=Maple, age=40, health_status=AT_RISK, forest=None)
