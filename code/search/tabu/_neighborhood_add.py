
from search.tabu._neighborhood_abstract import NeighborhoodAbstract

class NeighborhoodAdd(NeighborhoodAbstract):
    def __init__(self, database, **kwargs):
        super().__init__(database, 'Add', **kwargs)

    def _scan(self, solution):
        # Insert missing courses
        for (course, missing) in solution.missing_courses():
            for time_room in solution.avaliable_slots():
                combination = (course, ) + time_room

                # Check for tabu
                if self.is_tabu(combination): continue

                # Create simulated solution
                yield (combination, solution.simulate_add(*combination))

    def _inverse(self, move):
        # TODO: think about the inverse of add
        return move

    def _apply(self, solution, combination, penalties, objective):
        solution.mutate_add(*combination, penalties=penalties)
