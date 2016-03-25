
class Penalties:
    def __init__(self, U=0, W=0, A=0, P=0, V=0):
        self.U_sum = U
        self.W_sum = W
        self.A_sum = A
        self.P_sum = P
        self.V_sum = V

    def copy(self):
        return Penalties(self.U_sum, self.W_sum, self.A_sum, self.P_sum, self.V_sum)

    def dict(self):
        return {
            'U_sum': self.U_sum,
            'W_sum': self.W_sum,
            'A_sum': self.A_sum,
            'P_sum': self.P_sum,
            'V_sum': self.V_sum
        }

    def cost(self):
        return 10 * self.U_sum + 5 * self.W_sum + 2 * self.A_sum + self.P_sum + self.V_sum

    # defines self == other
    def __eq__(self, other):
        return isinstance(other, Penalties) and (
            self.U_sum == other.U_sum and self.W_sum == other.W_sum and
            self.A_sum == other.A_sum and self.P_sum == other.P_sum and
            self.V_sum == other.V_sum
        )

    # defines self += other
    def __iadd__(self, other):
        if isinstance(other, Penalties):
            self.U_sum += other.U_sum
            self.W_sum += other.W_sum
            self.A_sum += other.A_sum
            self.P_sum += other.P_sum
            self.V_sum += other.V_sum
            return self
        elif other == 0:
            return self
        else:
            return NotImplemented

    # defines new = self + other
    def __add__(self, other):
        if isinstance(other, Penalties):
            new = self.copy()
            return Penalties.__iadd__(new, other)
        elif other == 0:
            return self.copy()
        else:
            return NotImplemented

    # defines new = other + self
    def __radd__(self, other):
        if isinstance(other, Penalties):
            return Penalties.__add__(self, other)
        elif other == 0:
            return self.copy()
        else:
            return NotImplemented
