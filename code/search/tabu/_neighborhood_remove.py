
from search.tabu._neighborhood_abstract import NeighborhoodAbstract

class NeighborhoodRemove(NeighborhoodAbstract):
    def __init__(self, database, **kwargs):
        super().__init__(database, 'Remove', **kwargs)

    def _scan(self, solution):
        # Remove existing course
        for combination in solution.existing_combinations():
            # Check for tabu
            if self.is_tabu(combination): continue

            # Create simulated solution
            yield (combination, solution.simulate_remove(*combination))

    def _inverse(self, move):
        # TODO: think about the inverse of remove
        return move

    def _apply(self, solution, combination, penalties, objective):
        solution.mutate_remove(*combination, penalties=penalties)
