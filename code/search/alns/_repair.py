
from search.alns._mutate_abstract import MutateAbstraction

class Repair(MutateAbstraction):
    def __init__(self, **kwargs):
        methods = [
            'greedy'
        ]

        super().__init__(methods, **kwargs)

    def greedy(self, solution, **kwargs):
        # Insert missing courses
        for course in solution.missing_courses():
            for time_room in solution.avaliable_slots():
                combination = (course, ) + time_room

                # Create simulated solution
                penalties = solution.simulate_add(*combination)

                # If valid and better
                if penalties is not None:
                    if penalties.cost() < 0:
                        solution.mutate_add(*combination, penalties=penalties)
