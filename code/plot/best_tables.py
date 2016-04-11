
from _setup import results_path

from tabulate import tabulate

import gridsearch

def format_tabel(mean, stddev, row_names, row_header, col_names, col_header, caption):
    header = [
        ['', '', '\\multicolumn{%d}{c}{\\texttt{%s}}' % (len(col_names), col_header)],
        ['', ''] + list(map(str, col_names))
    ]

    output = []
    for name, mean_row, stddev_row in zip(row_names, mean, stddev):
        formatted = [
            '(%.2f, %.2f)' % (m, s) for m, s in zip(mean_row, stddev_row)
        ]
        output.append(['', str(name)] + formatted)
    output[0][0] = '\\multirow{%d}{*}{\\texttt{%s}}' % (len(row_names), row_header)

    formatted = ''
    formatted += '\\begin{table}[H]\n'
    formatted += '\\centering\n'
    formatted += '\\centerline{\\begin{tabular}{rr|%s}\n' % ('c' * len(col_names))

    for h in header:
        formatted += ' & '.join(h) + '\\\\ \n'
    formatted += '\\hline\n'

    for o in output:
        formatted += ' & '.join(o) + '\\\\ \n'

    formatted += '\\end{tabular}}\n'
    formatted += '\\caption{%s}\n' % caption
    formatted += '\\end{table}\n'

    return formatted

def format_subset(select, algorithm):
    mean = algorithm.mean()
    stddev = algorithm.stddev()
    best = algorithm.best_index()
    parameters = algorithm.parameters
    keys = list(parameters.keys())

    # Assume there are 4 parameters
    if len(best) != 4:
        raise ValueError('assuming 4 parameters')

    # Create numpy subset
    subset = list(best)
    subset[select[0]] = slice(None)
    subset[select[1]] = slice(None)

    rest = sorted(list(set(range(0, 4)) - set(select)))

    # Fixing last two
    return format_tabel(
        mean[subset],
        stddev[subset],
        row_names=parameters[keys[select[0]]],
        row_header=keys[select[0]].replace('_', '\\_'),
        col_names=parameters[keys[select[1]]],
        col_header=keys[select[1]].replace('_', '\\_'),
        caption='Shows $(\\mu, \\sigma)$ with \\texttt{%s=%s} and \\texttt{%s=%s} fixed' % (
            keys[rest[0]].replace('_', '\\_'), parameters[keys[rest[0]]][best[rest[0]]],
            keys[rest[1]].replace('_', '\\_'), parameters[keys[rest[1]]][best[rest[1]]]
        )
    )


alns, tabu = gridsearch.Analyse.load(
    results_path('alns.npy'),
    results_path('tabu.npy')
)

# Fixing last two
print(format_subset([0, 1], tabu))
print(format_subset([2, 3], tabu))

print(format_subset([0, 3], alns))
print(format_subset([1, 2], alns))
