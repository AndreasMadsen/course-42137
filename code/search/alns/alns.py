
import time
import random

from search.alns._repair import Repair
from search.alns._destroy import Destroy
from search._search_abstract import SearchAbstract

class ALNS(SearchAbstract):
    def __init__(self, database, initial, verbose=False, **kwargs):
        """Standard implementation of ALNS

        Parameters
        ----------
        database: the database object (required)
        initial: the initial solution, this will not be mutated (required)

        verbose: if true, progress information will be printed to stdout
                 (default: False)

        update_lambda: the remember parameter used for updateing the heuristic
                       selection properbilities (default: 0.9)
        w_global: psi gain for a globally better solution (default: 10)
        w_current: psi gain for an improved solution when comparing with last
                   iteration (default: 5)
        w_accept: psi gain for accepting a solution, not used! (default: 1)
        w_reject: psi gain for rejecting a solution, not used! (default: 0)

        remove: how many (course, time, room) combination there should be
                removed in each destroy operation. (default: 5)

        Attributes
        ----------
        interations: the number of iterations performed
        solution: the globally best solution
        """
        super().__init__(database, initial, **kwargs)

        self._current = initial.copy()

        self._repair = Repair(database, **kwargs)
        self._destroy = Destroy(database, **kwargs)

    def search(self, max_duration):
        """search for a better solution, the time usage may not exceed
        `max_duration` seconds.
        """
        max_time = time.clock() + max_duration

        while(time.clock() < max_time):
            if (self._verbose): tick = time.clock()
            old_objective = self._current.objective

            # Destroy and repair solution
            destroy_method = self._destroy.execute_mutateor(self._current)
            repair_method = self._repair.execute_mutateor(self._current)
            self._print('- used destroy method %s' % destroy_method)
            self._print('- used repair method %s' % repair_method)

            # Update properbilities
            is_better = {
                'global_better': self._current.objective < self.solution.objective,
                'current_better': self._current.objective < old_objective
            }
            self._destroy.update_properbilities(destroy_method, **is_better)
            self._repair.update_properbilities(repair_method, **is_better)

            # Update global solution
            solution_updated = False
            if self._current.objective < self.solution.objective:
                self.solution = self._current.copy()
                solution_updated = True

            self.iterations += 1

            if (self._verbose):
                self._print('iteration %d took %.2f sec' % (self.iterations, time.clock() - tick))

            if solution_updated:
                self._print('- new objective value %d' % self.solution.objective)

        self._print('done! objective value: %d' % self.solution.objective)
        self._print(self._destroy)
        self._print(self._repair)
