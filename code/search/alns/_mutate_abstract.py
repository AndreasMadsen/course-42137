
import random
import bisect

class MutateAbstraction:
    def __init__(self, methods, update_lambda=0.9,
                 w_global=10, w_current=5, w_accept=1, w_reject=0,
                 **kwargs):

        self._update_lambda = update_lambda
        self._w_global = w_global
        self._w_current = w_current
        self._w_accept = w_accept
        self._w_reject = w_reject

        self._rho = [1] * len(methods)
        self._methods = methods

        self._settings = kwargs

    def _calculate_cdf(self):
        rho_sum = sum(self._rho)
        cumsum = 0
        cdf = []
        for rho in self._rho:
            cumsum += rho
            cdf.append(cumsum / rho_sum)
        return cdf

    def execute_mutateor(self, solution):
        index = bisect.bisect(self._calculate_cdf(), random.random())
        getattr(self, self._methods[index])(solution, **self._settings)
        return self._methods[index]

    def update_properbilities(self, method,
                              global_better=False, current_better=False,
                              accept=False, reject=False):
        psi = 0
        if global_better and psi < self._w_global: psi = self._w_global
        if current_better and psi < self._w_current: psi = self._w_current
        if accept and psi < self._w_accept: psi = self._w_accept
        if reject and psi < self._w_reject: psi = self._w_reject

        index = self._methods.index(method)
        self._rho[index] = self._update_lambda * self._rho[index] \
            + (1 - self._update_lambda) * psi

    def __str__(self):
        rho_sum = sum(self._rho)
        stats = '\n'.join(
            '  %s: %.3f' % (method, self._rho[i] / rho_sum)
            for i, method in enumerate(self._methods)
        )
        return type(self).__name__ + ' stats:\n' + stats
