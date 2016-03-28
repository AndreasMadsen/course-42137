
from search.tabu._neighborhood_abstract import NeighborhoodAbstract

class NeighborhoodAddRemove(NeighborhoodAbstract):
    def __init__(self, database, **kwargs):
        super().__init__(database, 'AddRemove', **kwargs)

    def _scan(self, solution):
        # Insert missing courses
        for (course, missing) in solution.missing_courses():
            for time_room in solution.avaliable_slots():
                combination = (course, ) + time_room

                # Check for tabu
                move = (True, combination)
                if self.is_tabu(move): continue

                # Create simulated solution
                yield (move, solution.simulate_add(*combination))

        # Remove existing course
        for combination in solution.existing_combinations():
            # Check for tabu
            move = (False, combination)
            if self.is_tabu(move): continue

            # Create simulated solution
            yield (move, solution.simulate_remove(*combination))

    def _inverse(self, move):
        (added, combination) = move
        return (not added, combination)

    def _apply(self, solution, move, penalties, objective):
        (added, combination) = move
        if added:
            solution.mutate_add(*combination, penalties=penalties)
        else:
            solution.mutate_remove(*combination, penalties=penalties)
