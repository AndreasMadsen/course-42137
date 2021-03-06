
import _setup

import dataset
import solution
import search
import judge

database = dataset.Database.from_id(1)
init_solution = solution.Solution(database)
solution.initialize(init_solution)

# perform tabu search
tabu = search.TABU(
    database, init_solution,
    allow_swap='dynamic', tabu_limit=40,
    diversification=5, intensification=10,
    verbose=True
)
tabu.search(30)

# Validate solution
v = judge.Validator(database, tabu.solution)
assert v.valid
assert v.correct

print(tabu.solution)
