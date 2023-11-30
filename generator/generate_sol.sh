#!/usr/bin/env sh

for L in `seq 8 2 20`; do
    for seed in `seq 0 500`; do
        python3 solver.py instances/multiple_L/L${L}/N${L}_d0.8_s${seed}.json > instances/multiple_L/L${L}/N${L}_d0.8_s${seed}.sol
    done
done
