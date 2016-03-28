
from search.tabu._neighborhood_abstract import NeighborhoodAbstract

class NeighborhoodSwap(NeighborhoodAbstract):
    def __init__(self, database, **kwargs):
        super().__init__(database, 'Swap', **kwargs)

    def _scan(self, solution):
        # Swap combinations
        for combination_a in solution.existing_combinations():
            for combination_b in solution.existing_combinations():
                # swap(A, B) is equal to swap(B, A) so test only one version
                if combination_a < combination_b: continue

                # Check for tabu
                move = (combination_a, combination_b)
                if self.is_tabu(move): continue

                # Create simulated solution
                yield (move, solution.simulate_swap(combination_a, combination_b))

    def _inverse(self, move):
        (combination_a, combination_b) = move
        # Create new combinations
        a_on_b = (combination_a[0], ) + combination_b[1:]
        b_on_a = (combination_b[0], ) + combination_a[1:]
        # Return as tuple with smallest first
        return (b_on_a, a_on_b) if b_on_a < a_on_b else (a_on_b, b_on_a)

    def _apply(self, solution, move, penalties, objective):
        solution.mutate_swap(*move, penalties=penalties)
