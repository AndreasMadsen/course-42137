#!/bin/sh
#PBS -N grid-search
#PBS -l walltime=08:30:00
#PBS -l nodes=1:ppn=1
#PBS -m eba
#PBS -M amwebdk@gmail.com

cd $PBS_O_WORKDIR

export PYTHONPATH=
source ~/stdpy3/bin/activate

python grid-search.py
