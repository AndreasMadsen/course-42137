
class SearchAbstract:
    def __init__(self, database, initial, verbose=False, **kwargs):
        self._database = database
        self._verbose = verbose

        self.iterations = 0
        self.solution = initial.copy()

    def _print(self, *msg):
        if (self._verbose): print(*msg)
