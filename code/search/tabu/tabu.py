
import time

from search.tabu._neighborhood_add import NeighborhoodAdd
from search.tabu._neighborhood_remove import NeighborhoodRemove
from search.tabu._neighborhood_swap import NeighborhoodSwap
from search.tabu._neighborhood_move import NeighborhoodMove

class TABU:
    def __init__(self, database, initial, allow_swap=False, verbose=False):
        self._database = database
        self._verbose = verbose

        self._add = NeighborhoodAdd(database)
        self._remove = NeighborhoodRemove(database)
        self._swap = NeighborhoodSwap(database)
        self._move = NeighborhoodMove(database)

        self._allow_swap = allow_swap

        self.iterations = 0
        self.solution = initial.copy()

    def _print(self, *msg):
        if (self._verbose): print(*msg)

    def search(self, max_duration):
        max_time = time.clock() + max_duration

        while(time.clock() < max_time):
            if (self._verbose): tick = time.clock()

            # Swap can as such be done by performing 3 moves. Futhermore
            # it is quite expensive to search the neighborhood.
            if allow_swap:
                moves = [
                    self._add.scan_neighborhood(self.solution),
                    self._swap.scan_neighborhood(self.solution),
                    self._move.scan_neighborhood(self.solution),
                    self._remove.scan_neighborhood(self.solution)
                ]
            else:
                moves = [
                    self._add.scan_neighborhood(self.solution),
                    self._move.scan_neighborhood(self.solution),
                    self._remove.scan_neighborhood(self.solution)
                ]

            best_move = min(*moves, key=lambda move: move.objective)

            if best_move.objective < 0:
                if self._add.move_belongs(best_move):
                    self._add.apply(self.solution, best_move)

                elif self._allow_swap and self._swap.move_belongs(best_move):
                    self._swap.apply(self.solution, best_move)

                elif self._move.move_belongs(best_move):
                    self._move.apply(self.solution, best_move)

                elif self._remove.move_belongs(best_move):
                    self._remove.apply(self.solution, best_move)

            self.iterations += 1

            if (self._verbose):
                self._print("iteration %d took %.2f sec" % (self.iterations, time.clock() - tick))

            if best_move.objective < 0:
                self._print('- new objective value: %d' % self.solution.objective)
                self._print('- used: %s' % type(best_move).__name__.lower())
            else:
                break

        self._print('done! objective value: %d' % self.solution.objective)
