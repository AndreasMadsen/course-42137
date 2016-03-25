
import time

class Tabu:
    def __init__(self, database, initial, verbose=False):
        self._database = database
        self._verbose = verbose

        self._swap_tabu = set()
        self._move_tabu = set()
        self._insert_tabu = set()
        self._remove_tabu = set()

        self.iterations = 0
        self.solution = initial

    def _print(self, *msg):
        if (self._verbose): print(*msg)

    def _day_period_room(self, day=-1, period=-1, room=-1):
        for d in range(day + 1, self._database.days):
            for p in range(period + 1, self._database.periods_per_day):
                for r in range(room + 1, self._database.rooms):
                    yield (d, p, r)

    def search(self, max_duration):
        max_time = time.clock() + max_duration
        solution_updated = False

        while(time.clock() < max_time):
            if (self._verbose): tick = time.clock()
            solution_updated = False

            # Insert missing courses
            for course in self.solution.missing_courses():
                for time_room in self._day_period_room():
                    combination = (course, ) + time_room
                    # Check for tabu
                    if combination in self._insert_tabu:
                        continue

                    # Create simulated solution
                    penalties = self.solution.simulate_add(*combination)

                    # If valid and better
                    if penalties is not None:
                        if penalties.cost() < 0:
                            # Add to tabu and update solution
                            self._insert_tabu.add(combination)
                            self.solution.mutate_add(*combination, penalties=penalties)
                            solution_updated = True

            # Swap combinations
            for combination_a in self.solution.existing_combinations():
                for combination_b in self.solution.existing_combinations():
                    # swap(A, B) is equal to swap(B, A) so test only one version
                    if combination_a[0] == combination_b[0] or \
                       combination_a[1] >= combination_b[1] or \
                       combination_a[2] >= combination_b[2] or \
                       combination_a[3] >= combination_b[3]:
                        continue

                    # Check for tabu
                    if combination_a[1:] + combination_b[1:] in self._swap_tabu:
                        continue

                    # Create simulated solution
                    penalties = self.solution.simulate_swap(combination_a, combination_b)

                    # If valid and better
                    if penalties is not None:
                        if penalties.cost() < 0:
                            # Add to tabu and update solution
                            self._swap_tabu.add(combination_a[1:] + combination_b[1:])
                            self.solution.mutate_swap(
                                combination_a, combination_b,
                                penalties=penalties
                            )
                            solution_updated = True

                            # if A is swaped to B, it won't make sense to later
                            # swap A to C. So stop searching for swaps with
                            # A combination.
                            break

            # Move combination
            for combination in self.solution.existing_combinations():
                for time_period in self._day_period_room():
                    # Check for tabu
                    if combination[1:] + time_period in self._move_tabu:
                        continue

                    # Create simulated solution
                    simulation = self.solution.copy()
                    simulation.swap(combination[1:], time_period)

                    # If valid and better
                    if simulation.valid():
                        if simulation.cost() < self.solution.objective:
                            # Add to tabu and update solution
                            self._move_tabu.add(combination[1:] + time_period)
                            self.solution = simulation
                            solution_updated = True

                            # if A is swaped to B, it won't make sense to later
                            # swap A to C. So stop searching for swaps with
                            # A combination.
                            break

            # Remove existing course
            for combination in self.solution.existing_combinations():
                # Check for tabu
                if combination in self._remove_tabu:
                    continue

                # Create simulated solution
                penalties = self.solution.simulate_remove(*combination)

                # If valid and better
                if penalties is not None:
                    if penalties.cost() < 0:
                        # Add to tabu and update solution
                        self._remove_tabu.add(combination)
                        self.solution.mutate_remove(*combination, penalties=penalties)
                        solution_updated = True

            self.iterations += 1

            if (self._verbose):
                self._print("iteration %d took %d sec" % (self.iterations, time.clock() - tick))

            if (solution_updated is False):
                return
