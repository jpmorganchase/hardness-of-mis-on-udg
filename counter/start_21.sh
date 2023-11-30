for L in 21; do
    for r in 6.083 6.325; do
        for seed in `seq 0 1000`; do #1.0 1.415 2.0 2.237 2.829 3.0
            python3 ../generator/generate.py -L $L -s $seed -r $r --metis -f test
        done
    done
done

for N in 353; do
    for r in 6.083 6.325; do
        for seed in `seq 0 1000`; do
            (time ./gs_counter test/N${N}_d0.8_s${seed}_r${r}.txt >> data/N${N}_d0.8_r${r}.res) 2>> data/N${N}_d0.8_r${r}.time
        done
    done
done