
import sys
import os.path as path
import pickle
import textwrap

import numpy as np

class Analyse:
    def __init__(self, results, parameters, best_objective):
        self.results = self._scale_results(results, best_objective)
        self.parameters = parameters

    def _scale_results(self, results, best_objective):
        scaled = np.zeros((results.shape[0], ) + results.shape[2:])
        n_datasets = results.shape[1]
        for i in range(0, n_datasets):
            scaled += (results[:, i] - best_objective[i]) / (best_objective[i] * n_datasets)
        return scaled

    def mean(self):
        return np.mean(self.results, axis=0)

    def stddev(self):
        return np.std(self.results, axis=0)

    def select_trails(self, index):
        return self.results[(slice(None), ) + index]

    def best_index(self):
        mean_results = self.mean()
        return np.unravel_index(np.argmin(mean_results), mean_results.shape)

    def index_to_settings(self, index):
        settings = dict()
        index = iter(index)
        for key, values in self.parameters.items():
            if len(values) == 1:
                settings[key] = values[0]
            else:
                settings[key] = values[next(index)]
        return settings

    def best_settings(self):
        return self.index_to_settings(self.best_index())

    def __str__(self):
        best_index = self.best_index()

        return textwrap.dedent("""
        Analysis:
            - trails: {trials}
            - shape: {shape}
            - parameter space:
                {parameters}
            - best settings:
                {best_settings}
            - best objective:
                mean: {best_mean}
                stddev: {best_stddev}
        """).format(
            trials=self.results.shape[0],
            shape=self.results.shape[1:],
            parameters=dict(self.parameters),
            best_settings=self.index_to_settings(best_index),
            best_mean=round(np.mean(self.select_trails(best_index)), 4),
            best_stddev=round(np.std(self.select_trails(best_index)), 4)
        )

    @classmethod
    def load(cls, *filepaths):
        objects_list = []
        results_list = []
        parameters_list = []

        # Load data
        for filepath in filepaths:
            (basepath, _) = path.splitext(filepath)

            results_list.append(np.load(basepath + '.npy'))
            with open(basepath + '.plk', 'rb') as f:
                parameters_list.append(pickle.load(f))

        # Calculate best objective
        best = Analyse.best_objective(*results_list)

        # Construct Analyse objects
        for results, parameters in zip(results_list, parameters_list):
            objects_list.append(Analyse(results, parameters, best))

        # Finish
        return objects_list

    @staticmethod
    def best_objective(*results_list):
        num_databases = results_list[0].shape[1]

        if len(results_list) == 1:
            return [
                np.min(results_list[0][:, i]) for i in range(0, num_databases)
            ]
        else:
            return [
                min(*[np.min(results[:, i]) for results in results_list])
                for i in range(0, num_databases)
            ]
