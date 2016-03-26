
import time
import random

def _random_sample(iterable, amount):
    if len(iterable) <= amount: return list(iterable)
    else: return random.sample(iterable, amount)

class ALNS:
    def __init__(self, database, initial, verbose=False,
                 destroy_coursed_removed=5):
        self._database = database
        self._verbose = verbose

        self.iterations = 0
        self.solution = initial.copy()
        self._current = initial.copy()

        self._destroy = {
            'coursed_removed': destroy_coursed_removed
        }

    def _print(self, *msg):
        if (self._verbose): print(*msg)

    def search(self, max_duration):
        max_time = time.clock() + max_duration

        while(time.clock() < max_time):
            if (self._verbose): tick = time.clock()
            solution_updated = False

            # Destroy: remove existing courses
            for combination in _random_sample(
                self._current.existing_combinations(),
                self._destroy['coursed_removed']
            ):
                self._current.mutate_remove(*combination)

                # update solution if better
                if self._current.objective < self.solution.objective:
                    self.solution = self._current.copy()
                    solution_updated = True

            # Repair: Insert missing courses
            for course in self._current.missing_courses():
                for time_room in self._current.avaliable_slots():
                    combination = (course, ) + time_room

                    # Create simulated solution
                    penalties = self._current.simulate_add(*combination)

                    # If valid and better
                    if penalties is not None:
                        if penalties.cost() < 0:
                            self._current.mutate_add(*combination, penalties=penalties)

                            # update solution if better
                            if self._current.objective < self.solution.objective:
                                self.solution = self._current.copy()
                                solution_updated = True

            self.iterations += 1

            if (self._verbose):
                self._print('iteration %d took %d sec' % (self.iterations, time.clock() - tick))

            if solution_updated:
                self._print('- new objective value %d' % self.solution.objective)

        self._print('done! objective value: %d' % self.solution.objective)
