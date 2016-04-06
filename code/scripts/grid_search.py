#!/bin/sh

qsub "$(dirname $0)/grid_search_alns.sh"
qsub "$(dirname $0)/grid_search_tabu.sh"
