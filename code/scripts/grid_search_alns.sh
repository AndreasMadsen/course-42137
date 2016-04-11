#!/bin/sh
#PBS -N grid-search-alns
#PBS -l walltime=16:00:00
#PBS -l nodes=1:ppn=12
#PBS -m eba
#PBS -M amwebdk@gmail.com

cd $PBS_O_WORKDIR

export PYTHONPATH=
source ~/stdpy3/bin/activate

python code/scripts/grid_search_alns.py
