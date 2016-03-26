
import random

from search.alns._mutate_abstract import MutateAbstraction

def _sample(iterable, amount):
    if len(iterable) <= amount: return list(iterable)
    else: return random.sample(iterable, amount)

class Destroy(MutateAbstraction):
    def __init__(self, database, **kwargs):
        methods = [
            'fully_random',
            'curriculum',
            'day',
            'course'
        ]

        super().__init__(database, methods, **kwargs)

    def fully_random(self, solution, remove=5, **kwargs):
        # remove existing combinations
        for combination in _sample(solution.existing_combinations(), remove):
            solution.mutate_remove(*combination)

    def curriculum(self, solution, remove=5, **kwargs):
        # Get random curricula and associated courses
        curricula = random.randint(0, self._database.meta.curricula - 1)
        courses = set(self._database.curricula[curricula].courses)

        # Select combinations related to this curricula
        combinations = [
            combination for combination in solution.existing_combinations()
            if combination[0] in courses
        ]

        # remove combinations
        for combination in _sample(combinations, remove):
            solution.mutate_remove(*combination)

    def day(self, solution, remove=5, **kwargs):
        # Get random day
        day = random.randint(0, self._database.meta.days - 1)

        # Select combinations related to this curricula
        combinations = [
            combination for combination in solution.existing_combinations()
            if combination[1] == day
        ]

        # remove combinations
        for combination in _sample(combinations, remove):
            solution.mutate_remove(*combination)

    def course(self, solution, remove=5, **kwargs):
        # Get random day
        course = random.randint(0, self._database.meta.courses - 1)

        # Select combinations related to this curricula
        combinations = [
            combination for combination in solution.existing_combinations()
            if combination[0] == course
        ]

        # remove combinations
        for combination in _sample(combinations, remove):
            solution.mutate_remove(*combination)
