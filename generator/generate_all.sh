#!/usr/bin/env sh

for L in `seq 7 2 25`; do
  for seed in `seq 0 500`; do
    python3 generate.py -L $L -s $seed
  done
done
