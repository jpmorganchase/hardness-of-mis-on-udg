#!/usr/bin/env sh

python3 optimization/create_file.py -path L21_ER

for L in 21; do
    for seed in `seq 0 500`; do
        python3 generate_ER.py -L $L -s $seed --cplex
        python3 optimization/optimize.py -L $L -s $seed --TTS --ER -path L21_ER
    done
done


