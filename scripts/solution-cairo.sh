#!/bin/bash
#
# python3 kagome_solution.py -b ibm_cairo -t ibm_cairo -a EfficientSU2 -w 1.8 -i 175 -o NFT -q 27 >> out-cairo.txt &
# python3 kagome_solution.py -p ibm-q-ncsu/nc-state/grad-qc-class -b ibm_cairo -t ibm_cairo -q 27 >> out-cairo.txt &
# python3 kagome_solution.py -p ibm-q-ncsu/nc-state/grad-qc-class -b ibm_cairo -t ibm_cairo -q 27 -o GSLS -i 50 -w 1.4 >> out-cairo.txt &

dir=$HOME/vqe/solution
name=cairo
file=$dir/out-$name.txt

cd $dir

python3 $dir/kagome_solution.py -b ibm_cairo -t ibm_cairo -a EfficientSU2 -w 1.314 -s 4096 -q 27 >> $file &