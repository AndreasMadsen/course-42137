#!/usr/bin/python3

import sys
import time

import dataset
import solution
import search
import judge

database = dataset.Database(*sys.argv[1:8])
total_time = int(sys.argv[8])

# use 45 on Tabu and the rest on ALNS
time_for_tabu = 45
end_time_for_alns = time.time() + total_time - time_for_tabu

# Run ALNS multiply times
best_solution = solution.Solution(database)

while time.time() < end_time_for_alns:
    # reset solution
    init_solution = solution.Solution(database)
    solution.initialize(init_solution)

    # perform tabu search
    alns = search.ALNS(
        database, init_solution,
        update_lambda=0.99, remove=1,
        w_global=10, w_current=10
    )

    # Optimize solution the remaining time, but no more than 60 sec
    remaining_time = min(end_time_for_alns - time.time(), 60)
    alns.search(remaining_time)

    # Update best solution
    if (alns.solution.objective < best_solution.objective):
        best_solution = alns.solution

# Run Tabu search on the alns solution for the last 30 sec
tabu = search.TABU(
    database, best_solution,
    allow_swap='dynamic', tabu_limit=40,
    diversification=5, intensification=10
)
tabu.search(time_for_tabu)

# Print final solution
print(tabu.solution)
