
import time
import random

from search.alns._repair import Repair
from search.alns._destroy import Destroy

class ALNS:
    def __init__(self, database, initial, verbose=False, **kwargs):
        self._database = database
        self._verbose = verbose

        self.iterations = 0
        self.solution = initial.copy()
        self._current = initial.copy()

        self._repair = Repair(database, **kwargs)
        self._destroy = Destroy(database, **kwargs)

    def _print(self, *msg):
        if (self._verbose): print(*msg)

    def search(self, max_duration):
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
