
import time
import random

from search.tabu._neighborhood_add_remove import NeighborhoodAddRemove
from search.tabu._neighborhood_swap import NeighborhoodSwap
from search.tabu._neighborhood_move import NeighborhoodMove
from search._search_abstract import SearchAbstract

class TABU(SearchAbstract):
    def __init__(self, database, initial,
                 diversification=None, intensification=None,
                 tabu_limit=None, allow_swap=True,
                 **kwargs):
        """Standard implementation of TABU

        Parameters
        ----------
        database: the database object (required)
        initial: the initial solution, this will not be mutated (required)

        verbose: if true, progress information will be printed to stdout
                 (default: False)

        diversification: If the current iteration did not improve the solution
                         then diversify the solution by removing
                         `diversification` amount of random (course, time, room)
                         combinations from the schedule. If None diversification
                         is disabed. (default: None)

        intensification: If the globally best solution hasn't improved for
                         `intensification` amount of iteration. Then reset the
                         current solution to be currently globally best
                         solution, and clear the tabu memory. If None
                         intensification is disabed. (default: None)

        tabu_limit: Limits the tabu memory to `tabu_limit` move. A new move
                    will remove the oldest move from the tabu memory. Note that
                    the memory of move, swap and add+remove are independent,
                    this is to simplify the implementation. If None there is no
                    memory limit. (default. None)

        allow_swap: If true swap operations are included in the neighborhood.
                    Otherwise only move and add+remove operations are included.
                    (default: False)

        Attributes
        ----------
        interations: the number of iterations performed
        solution: the globally best solution
        """
        super().__init__(database, initial, **kwargs)

        self._current = initial.copy()

        self._add_remove = NeighborhoodAddRemove(database, tabu_limit=tabu_limit)
        self._swap = NeighborhoodSwap(database, tabu_limit=tabu_limit)
        self._move = NeighborhoodMove(database, tabu_limit=tabu_limit)

        self._allow_swap = allow_swap
        self._diversification = diversification
        self._intensification = intensification
        self._iters_without_improved_global = 0

    def _intensity(self):
        if self._intensification is None: return False
        if self._iters_without_improved_global < self._intensification: return False

        # Reset tabo
        self._add_remove.clear_tabu()
        self._swap.clear_tabu()
        self._move.clear_tabu()

        # Update current solution
        self._current = self.solution.copy()

        # Indicate that intensification was performed
        return True

    def _diversify(self):
        if self._diversification is None: return False

        # sample `diversification` amount of combinations to remove
        existing = self._current.existing_combinations()
        if len(existing) <= self._diversification:
            to_remove = list(existing)
        else:
            to_remove = random.sample(existing, self._diversification)

        # remove existing combinations
        for combination in to_remove:
            self._current.mutate_remove(*combination)

        # Indicate that diversification was performed
        return True

    def search(self, max_duration):
        """search for a better solution, the time usage may not exceed
        `max_duration` seconds.
        """
        max_time = time.clock() + max_duration

        while(time.clock() < max_time):
            if (self._verbose): tick = time.clock()

            # Track if diversification or intensification is performed
            did_diversification = False
            did_intensification = False

            # Swap can as such be done by performing 3 moves. Futhermore
            # it is quite expensive to search the neighborhood.
            moves = [
                self._add_remove.scan_neighborhood(self._current),
                self._move.scan_neighborhood(self._current)
            ]
            if self._allow_swap:
                moves.append(self._swap.scan_neighborhood(self._current))

            # Find the best move
            best_move = min(*moves, key=lambda move: move.objective)

            # Apply the best move if it decreases the objective
            if best_move.objective < 0:
                if self._add_remove.move_belongs(best_move):
                    self._add_remove.apply(self._current, best_move)

                elif self._move.move_belongs(best_move):
                    self._move.apply(self._current, best_move)

                elif self._swap.move_belongs(best_move):
                    self._swap.apply(self._current, best_move)
            # no better solution was found intenify and diversify
            else:
                did_intensification = self._intensity()
                did_diversification = self._diversify()

            # Update global solution
            solution_updated = False
            if self._current.objective < self.solution.objective:
                self._iters_without_improved_global = 0
                self.solution = self._current.copy()
                solution_updated = True
            else:
                self._iters_without_improved_global += 1

            self.iterations += 1

            # Print verbose output
            if (self._verbose):
                self._print("iteration %d took %.2f sec" % (self.iterations, time.clock() - tick))
                self._print('- without improved solution: %d' % self._iters_without_improved_global)

            if solution_updated:
                self._print('- new objective value: %d' % self.solution.objective)

            if best_move.objective < 0:
                self._print('- used: %s' % type(best_move).__name__.lower())
            elif did_diversification or did_intensification:
                if did_intensification: self._print(' - intensified solution')
                if did_diversification: self._print(' - diversified solution')

            # Stop search
            if best_move.objective >= 0 and not did_diversification and not did_intensification:
                break

        self._print('done! objective value: %d' % self.solution.objective)
