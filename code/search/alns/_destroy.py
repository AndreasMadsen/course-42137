
import random

from search.alns._mutate_abstract import MutateAbstraction

def _sample(iterable, amount):
    if len(iterable) <= amount: return list(iterable)
    else: return random.sample(iterable, amount)

class Destroy(MutateAbstraction):
    def __init__(self, **kwargs):
        methods = [
            'fully_random'
        ]

        super().__init__(methods, **kwargs)

    def fully_random(self, solution, courses_removed=5, **kwargs):
        # remove existing courses
        for combination in _sample(solution.existing_combinations(), courses_removed):
            solution.mutate_remove(*combination)
