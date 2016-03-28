
import collections

class NeighborhoodAbstract:
    def __init__(self, database, name, tabu_limit=None):
        self._database = database
        self._tabu = set()
        self._MoveObject = collections.namedtuple(name, ['move', 'penalties', 'objective'])

    def is_tabu(self, move):
        return move in self._tabu

    def scan_neighborhood(self, solution):
        best_move = None
        best_penalties = None
        best_objective = 0

        for move, penalties in self._scan(solution):
            # If valid and better
            if penalties is not None and penalties.cost() < best_objective:
                # Update best move and associated information
                best_move = move
                best_penalties = penalties
                best_objective = penalties.cost()

        # Return the best move
        return self._MoveObject(best_move, best_penalties, best_objective)

    def move_belongs(self, move_object):
        return isinstance(move_object, self._MoveObject)

    def apply(self, solution, move_object):
        self._tabu.add(self._inverse(move_object.move))
        self._apply(solution, *move_object)
