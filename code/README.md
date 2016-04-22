# University Timetabling
_By: Andreas Madsen (s123598)_

### Requirements

* python 3.5 or 3.4
* numpy (only used in gridsearch for storing results)
* nose (only used in test for running tests)
* tabulate (only used in plot for generating latex tables)

This install script will setup python 3 on the HPC cluster, but it is much
more complicated that what is needed for this project:
https://github.com/AndreasMadsen/my-setup/tree/master/dtu-hpc-python3

### Running the solver

```shell
python3 ./solver.py courses.utt lecturers.utt rooms.utt curricula.utt relation.utt unavailability.utt 300
```

### Examples

* `scripts/inspect_tabu.py` will run a single optimization on the first dataset using TABU
* `scripts/inspect_alns.py` will run a single optimization on the first dataset using ALNS
* `scripts/grid_search_tabu.py` the grid search script used for the TABU optimization
* `scripts/grid_search_alns.py` the grid search script used for the ALNS optimization
* `scripts/test_tabu.py` the test script used for the TABU optimization
* `scripts/test_alns.py` the test script used for the ALNS optimization

### Directories

The code is structured into the following directories:

* `dataset`: contains `Database` constructor, used for initializing a dataset
* `gridsearch`: code for running many optimizations using different parameters
* `judge`: code for validating the solution using `Judge.exe`.
* `plot`: code for generating latex tables and other summaries
* `script`: scripts used for maunal inspecting and running on the HPC cluster
* `search`: the ALNS and TABU implementations are in here
* `solution`: contains `Solution` constructor that constains the an solution. Its
 methods simulate moves or mutate the solution. It also contains the random
 initialization procedure.
* `test`: test scripts, run them using `make test`
