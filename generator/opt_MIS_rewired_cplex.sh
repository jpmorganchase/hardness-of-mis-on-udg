#!/usr/bin/env sh

python3 optimization/create_file_rewired.py -path L21_rewired
python3 generate_rewired_graph.py

for L in 21; do
    for r in 1.415; do
        for seed in `seq 0 20`; do
            for p in `seq 1 20`; do
                python3 optimization/optimize.py -L $L -s $seed -r $r --TTS -path L21_rewired -rewiring_frac $p
            done
        done
    done
done


