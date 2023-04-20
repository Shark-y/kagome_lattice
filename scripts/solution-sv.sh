#!/bin/bash
#
# python kagome_solution.py -b simulator_statevector -a POWELL -w 1.0 -s 4096
# python kagome_solution.py -p ibm-q-ncsu/nc-state/grad-qc-class -b simulator_statevector

dir=$HOME/vqe/solution
name=sv
file=$dir/out-$name.txt

cd $dir

python3 $dir/kagome_solution.py -b simulator_statevector -a EfficientSU2 -w 1.31 -s 4096 -q 16 >> $file &