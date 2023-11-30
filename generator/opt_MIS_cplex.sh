#!/usr/bin/env sh

python3 optimization/create_file.py -path L21_diff_radius_UDG_3

for L in 21; do
    for r in 1.0 1.415 2.0 2.237 2.829 3.0 3.163 3.606 4.0 4.124 4.243 4.473 5.0 5.1 5.386 5.657 5.831 6.0 6.083 6.325 6.404 6.709 7.0 7.072 7.212 7.281 7.616 7.811 8.0 8.063 8.247 8.486 8.545 8.603 8.945 9.0 9.056 9.22 9.434 9.487 9.849 9.9; do
        for seed in `seq 0 40`; do
            python3 generate.py -L $L -s $seed -r $r --cplex
            python3 optimization/optimize.py -L $L -s $seed -r $r --TTS -path L21_diff_radius_UDG_8cores
        done
    done
done


