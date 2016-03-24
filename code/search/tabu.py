
import time

class Tabu:
    def __init__(self, database, initial, verbose=False):
        self._database = database
        self._verbose = verbose

        self._swap_tabu = set()
        self._insert_tabu = set()
        self._remove_tabu = set()

        self.iterations = 0
        self.solution = initial
        self.objective = self.solution.cost()

    def _print(self, *msg):
        if (self._verbose): print(*msg)

    def _day_period_room(self, day=-1, period=-1, room=-1):
        for d in range(day + 1, self._database.days):
            for p in range(period + 1, self._database.periods_per_day):
                for r in range(room + 1, self._database.rooms):
                    yield (d, p, r)

    def _total_cost(self, U_sum, W_sum, A_sum, P_sum, V_sum):
        return 10 * U_sum + 5 * W_sum + 2 * A_sum + P_sum + V_sum

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
                    penalties = self.solution.simulate_add(*combination, full=True)

                    # If valid and better
                    if penalties is not None:
                        if self._total_cost(**penalties) < 0:
                            # Add to tabu and update solution
                            self._insert_tabu.add(combination)
                            self.solution.mutate_add(*combination, penalties=penalties)
                            self.objective = self.solution.objective
                            solution_updated = True

            # Switch courses
            for combination_a in self._day_period_room():
                for combination_b in self._day_period_room(*combination_a):
                    # Check for tabu
                    if combination_a + combination_b in self._swap_tabu:
                        continue

                    # Create simulated solution
                    simulation = self.solution.copy()
                    simulation.swap(combination_a, combination_b)

                    # If valid and better
                    if simulation.valid():
                        if simulation.cost() < self.objective:
                            # Add to tabu and update solution
                            self._swap_tabu.add(combination_a + combination_b)
                            self.solution = simulation
                            self.objective = simulation.cost()
                            solution_updated = True

            # Remove existing course
            for combination in self.solution.existing_combinations():
                # Check for tabu
                if combination in self._remove_tabu:
                    continue

                # Create simulated solution
                simulation = self.solution.copy()
                simulation.remove(combination)

                # If valid and better
                if simulation.valid():
                    if simulation.cost() < self.objective:
                        # Add to tabu and update solution
                        self._remove_tabu.add(combination)
                        self.solution = simulation
                        self.objective = simulation.cost()
                        solution_updated = True

            self.iterations += 1

            if (self._verbose):
                self._print("iteration %d took %d sec" % (self.iterations, time.clock() - tick))

            if (solution_updated is False):
                return
