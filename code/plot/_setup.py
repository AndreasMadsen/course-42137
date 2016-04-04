import sys
import os.path as path
import os

thisdir = path.dirname(path.realpath(__file__))
sys.path.append(path.join(thisdir, '../'))

results_dir = path.realpath(path.join(thisdir, '..', 'results'))

# Ensire results directory exists
if not path.isdir(results_dir): os.mkdir(results_dir)

def results_path(filename):
    return path.join(results_dir, filename)
