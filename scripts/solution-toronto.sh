#!/bin/bash
# python3 kagome_solution.py -p ibm-q-ncsu/nc-state/grad-qc-class -b ibmq_toronto -t ibmq_toronto -q 27 >> out-toronto.txt &
#
dir=$HOME/vqe/solution
name=geneva
file=$dir/out-$name.txt

cd $dir

python3 $dir/kagome_solution.py -b ibmq_toronto -t ibmq_toronto -a ExcitationPreserving -w -1.8992 -s 2048 -q 27 >> $file &