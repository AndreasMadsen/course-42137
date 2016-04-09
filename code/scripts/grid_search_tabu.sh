#!/bin/sh
#PBS -N grid-search-tabu
#PBS -l walltime=31:00:00
#PBS -l nodes=1:ppn=12
#PBS -m eba
#PBS -M amwebdk@gmail.com

cd $PBS_O_WORKDIR

export PYTHONPATH=
source ~/stdpy3/bin/activate

python code/scripts/grid_search_tabu.py
