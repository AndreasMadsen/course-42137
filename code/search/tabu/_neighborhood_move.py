
from search.tabu._neighborhood_abstract import NeighborhoodAbstract

class NeighborhoodMove(NeighborhoodAbstract):
    def __init__(self, database, **kwargs):
        super().__init__(database, 'Move', **kwargs)

    def _scan(self, solution):
        # Move combination
        for combination in solution.existing_combinations():
            for destination in solution.avaliable_slots():
                # Check for tabu
                move = (combination, destination)
                if self.is_tabu(move): continue

                # Create simulated solution
                yield (move, solution.simulate_move(combination, destination))

    def _inverse(self, move):
        (combination, destination) = move
        new_placement = (combination[0], ) + destination
        old_placement = combination[1:]
        return (new_placement, old_placement)

    def _apply(self, solution, move, penalties, objective):
        solution.mutate_move(*move, penalties=penalties)
