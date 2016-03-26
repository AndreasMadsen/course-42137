
import heapq

from search.alns._mutate_abstract import MutateAbstraction

class Repair(MutateAbstraction):
    def __init__(self, database, **kwargs):
        methods = [
            'very_greedy',
            'best_placement'
        ]

        super().__init__(database, methods, **kwargs)

    def very_greedy(self, solution, **kwargs):
        # Insert missing courses
        for (course, missing) in solution.missing_courses():
            for time_room in solution.avaliable_slots():
                combination = (course, ) + time_room

                # Create simulated solution
                penalties = solution.simulate_add(*combination)

                # If valid and better
                if penalties is not None:
                    if penalties.cost() < 0:
                        solution.mutate_add(*combination, penalties=penalties)

                        # Stop if all missing courses are inserted
                        missing -= 1
                        if missing == 0: break

    def best_placement(self, solution, **kwargs):

        # Evaluate all possibol placements for the given course
        def evaluate_improvement(course):
            for time_room in solution.avaliable_slots():
                combination = (course, ) + time_room

                # Create simulated solution
                penalties = solution.simulate_add(*combination)

                # add combination to to list of it improves the objective value
                if penalties is not None:
                    cost = penalties.cost()
                    if (cost < 0): yield (combination, cost)

        # Insert missing courses
        for (course, missing) in solution.missing_courses():
            # Get best combinations
            best = heapq.nsmallest(
                missing, evaluate_improvement(course),
                lambda v: v[1]
            )

            for combination, cost in best:
                # Redo the validation since the first validation was done
                # without continues mutation
                penalties = solution.simulate_add(*combination)
                # If valid and better
                if penalties is not None:
                    if penalties.cost() < 0:
                        solution.mutate_add(*combination, penalties=penalties)
