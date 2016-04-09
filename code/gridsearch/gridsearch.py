
import collections
import multiprocessing

import numpy as np

class GridSearch:
    def __init__(self, databases, initializer,
                 trials=3, time=3 * 60, workers=1,
                 dry_run=False, verbose=False, deep_verbose=False):

        self._databases = databases
        self._initializer = initializer

        self._trials = trials
        self._time = time
        self._workers = workers

        self._dry_run = dry_run
        self._verbose = verbose
        self._deep_verbose = deep_verbose

    def _print(self, *msg):
        if (self._verbose): print(*msg)

    def iterate_settings(self, parameters):
        # The dimention order of the numpy array assumes the key order is
        # concistent
        if not isinstance(parameters, collections.OrderedDict):
            raise TypeError('parameters should be an OrderedDict')

        yield from _generate_settings_and_index(parameters)

    def search(self, SearchAlgorithm, parameters):
        dims = (self._trials, len(self._databases)) + tuple(
            len(values) for values in parameters.values() if len(values) > 1
        )
        scores = np.zeros(dims)

        total_runs = scores.size
        current_runs = 1

        # Assume a paralization ratio of 0.8 and use Amdahl's law to calculated
        # expected time usage.
        scalability = 1 / (1 - 0.8 + (0.8 / self._workers))

        self._print('grid search using %s, expected time usage: %.2f hours' % (
            SearchAlgorithm.__name__, ((total_runs * self._time) / (3600 * scalability))
        ))

        with multiprocessing.Pool(processes=self._workers) as pool:
            for insert_index, settings, objective in \
                    pool.imap_unordered(
                        _benchmark,
                        self._itertate_runs(SearchAlgorithm, parameters)
                    ):

                self._print('- %d / %d, trail: %d, db: %d, using %s' % (
                    current_runs, total_runs, insert_index[0], insert_index[1], str(settings)
                ))
                scores[insert_index] = objective
                current_runs += 1

        return scores

    def _itertate_runs(self, SearchAlgorithm, parameters):
        for settings, index in self.iterate_settings(parameters):
            for i_database, database in enumerate(self._databases):
                for trail in range(0, self._trials):
                    yield (
                        (trail, i_database) + index,
                        SearchAlgorithm,
                        database,
                        self._initializer(database),
                        self._deep_verbose,
                        settings,
                        self._dry_run,
                        self._time
                    )

def _benchmark(args):
    # Unpack arguments
    (insert_index, SearchAlgorithm, database,
     init_solution, deep_verbose, settings,
     dry_run, time) = args

    # Create search algorithm
    algorithm = SearchAlgorithm(database, init_solution,
                                verbose=deep_verbose,
                                **settings)

    # Search solution
    if not dry_run:
        algorithm.search(time)

    # Return data used for verbose printing and result mapping
    return (insert_index, settings, algorithm.solution.objective)

def _generate_settings_and_index(parameters, keys=None, settings=dict(), index=tuple()):
    if keys is None: keys = list(reversed(list(parameters.keys())))
    else: keys = keys.copy()

    key = keys.pop()
    values = parameters[key]
    for i, value in enumerate(values):
        next_settings = settings.copy()
        next_settings[key] = value

        next_index = tuple(index) if len(values) == 1 else index + (i, )

        if len(keys) > 0:
            yield from _generate_settings_and_index(
                parameters, keys, next_settings, next_index
            )
        else:
            yield (next_settings, next_index)
