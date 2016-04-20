
import _setup

import dataset
import solution
import search
import judge

database = dataset.Database.from_id(1)
init_solution = solution.Solution(database)
solution.initialize(init_solution)

# perform tabu search
alns = search.ALNS(
    database, init_solution,
    update_lambda=0.99, remove=1,
    w_global=10, w_current=10,
    verbose=True
)
alns.search(30)

# Validate solution
v = judge.Validator(database, alns.solution)
assert v.valid
assert v.correct

print(alns.solution)
