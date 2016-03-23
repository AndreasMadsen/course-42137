
import time

class Tabu:
    def __init__(self, database, initial):
        self._database = database
        self._swap_tabu = set()
        self._insert_tabu = set()
        self._remove_tabu = set()

        self.iterations = 0
        self.solution = initial
        self.objective = self.solution.cost()

    def _day_period_room(self, day=-1, period=-1, room=-1):
        for d in range(day + 1, self._database.days):
            for p in range(period + 1, self._database.periods_per_day):
                for r in range(room + 1, self._database.rooms):
                    yield (d, p, r)

    def search(self, max_duration):
        max_time = time.clock() + max_duration
        solution_updated = False

        while(time.clock() < max_time):
            solution_updated = False

            # Insert missing courses
            for course in self.solution.missing_courses():
                for time_room in self._day_period_room():
                    combination = (course, ) + time_room
                    # Check for tabu
                    if combination in self._insert_tabu:
                        continue

                    # Create simulated solution
                    simulation = self.solution.copy()
                    simulation.insert(combination)

                    # If valid and better
                    if simulation.valid():
                        if simulation.cost() < self.objective:
                            # Add to tabu and update solution
                            self._insert_tabu.add(combination)
                            self.solution = simulation
                            self.objective = simulation.cost()
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

            if (solution_updated is False):
                return
