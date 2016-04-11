
import solution
import dataset

databases = [
    dataset.Database.from_id(db_id) for db_id in range(1, 14, 1)
]

def initalizer(database):
    initial_solution = solution.Solution(database)
    solution.initialize(initial_solution)
    return initial_solution
