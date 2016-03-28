
import re
import os
import os.path as path
import shutil
import subprocess

import solution

thisdir = path.dirname(path.realpath(__file__))

executable = path.join(thisdir, 'judge.exe')

tempdir = path.join(thisdir, 'temp')
solutionfile = path.join(tempdir, 'solution.sol')
penaltiesfile = path.join(tempdir, 'penalties.log')

extract_values = '^[A-Z]+\s*\|\s*((?:-|)[0-9]+)\s\|\s*((?:-|)[0-9]+)\s\|\s*((?:-|)[0-9]+)$'

class Validator:
    def __init__(self, database, solution):
        # Initalize validation holders
        self._valid = None
        self._correct = None
        self._actual_penalties = solution.penalties.copy()
        self._expected_penalties = None
        self._actual_objective = solution.objective
        self._expected_objective = None

        # Run validator
        self._reset_temp_dir()
        self._import_solution(solution)
        self._run_judge(database)

        if self.valid:
            self._load_penalties()
            self._correct = (self._actual_penalties == self._expected_penalties)
        else:
            self._correct = False

    @property
    def valid(self):
        return self._valid

    @property
    def correct(self):
        return self._correct

    def _reset_temp_dir(self):
        if path.exists(tempdir): shutil.rmtree(tempdir)
        os.mkdir(tempdir)

    def _import_solution(self, solution):
        with open(solutionfile, "w") as f:
            print(str(solution), file=f)

    def _run_judge(self, database):
        # if windows the .exe can be executed directly
        if os.name == 'nt':
            result = subprocess.run(
                [executable, database.directory, solutionfile],
                stdout=subprocess.PIPE,
                check=True, cwd=tempdir, universal_newlines=True)
        else:
            result = subprocess.run(
                ['mono', executable, database.directory, solutionfile],
                stdout=subprocess.PIPE,
                check=True, cwd=tempdir, universal_newlines=True)

        # Check if the solution is valid
        self._valid = 'RESULT CORRECT' in result.stdout

    def _load_penalties(self):
        calculated = []
        given = []

        with open(penaltiesfile, "r") as f:
            # skip first 4 lines
            for i in range(0, 4): next(f)
            for i in range(0, 6):
                result = re.search(extract_values, next(f))
                if result is None: raise Exception('could not parse penalties.log')
                calculated.append(int(result.group(1)))
                given.append(int(result.group(2)))

        self._expected_penalties = solution.Penalties(
            U=calculated[0],
            W=calculated[2],
            A=calculated[3],
            P=calculated[4],
            V=calculated[1]
        )
        self._expected_objective = calculated[5]
