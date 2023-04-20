#!/bin/bash

# python3 kagome_solution.py -p ibm-q-ncsu/nc-state/grad-qc-class -b ibm_geneva -t ibm_geneva -q 27 -o GSLS -i 100 -w -1.4 >> out-geneva.txt &

dir=$HOME/vqe/solution
name=geneva
file=$dir/out-$name.txt

cd $dir

python3 $dir/kagome_solution.py -b ibm_geneva -t ibm_geneva -a ExcitationPreserving -w -1.8992 -s 2048 -q 27 >> $file &