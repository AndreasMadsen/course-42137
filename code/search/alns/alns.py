
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

        self._repair = Repair(**kwargs)
        self._destroy = Destroy(**kwargs)

    def _print(self, *msg):
        if (self._verbose): print(*msg)

    def search(self, max_duration):
        max_time = time.clock() + max_duration

        while(time.clock() < max_time):
            if (self._verbose): tick = time.clock()
            solution_updated = False

            # Destroy solution
            old_objective = self._current.objective
            index = self._destroy.execute_mutateor(self._current)
            self._destroy.update_properbilities(
                index,
                global_better=(self._current.objective < self.solution.objective),
                current_better=(self._current.objective < old_objective)
            )

            # Repair solution
            old_objective = self._current.objective
            index = self._repair.execute_mutateor(self._current)
            self._repair.update_properbilities(
                index,
                global_better=(self._current.objective < self.solution.objective),
                current_better=(self._current.objective < old_objective)
            )

            # Update global solution
            if self._current.objective < self.solution.objective:
                self.solution = self._current.copy()
                solution_updated = True

            self.iterations += 1

            if (self._verbose):
                self._print('iteration %d took %d sec' % (self.iterations, time.clock() - tick))

            if solution_updated:
                self._print('- new objective value %d' % self.solution.objective)

        self._print('done! objective value: %d' % self.solution.objective)
