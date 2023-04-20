#!/bin/bash
# python3 kagome_solution.py -a ExcitationPreserving -w -1.5992 -s 4096 -q 16 >> out-guadalupe.txt &
# python3 kagome_solution.py -a EfficientSU2 -w 1.5992 >> out-guadalupe.txt &
# python3 kagome_solution.py -a EfficientSU2 -w 1.0 -o POWELL -up -1.0 -s 4096 >> out-guadalupe.txt &
# python3 kagome_solution.py -a EfficientSU2 -w 1.0 -o NFT -up -1.0 >> out-guadalupe.txt &
# python3 kagome_solution.py -p ibm-q-community/ibmquantumawards/open-science-22 -a EfficientSU2 -w 1.34 -o NFT -i 175 >> out-guadalupe.txt &
# python3 kagome_solution.py -p ibm-q-ncsu/nc-state/grad-qc-class -a EfficientSU2 -w 1.34 -o NFT -i 175 >> out-guadalupe.txt &
# python3 kagome_solution.py -p ibm-q-ncsu/nc-state/grad-qc-class >> out-guadalupe.txt &
# python3 kagome_solution.py -a EfficientSU2 -w 1.0 -o L_BFGS_B -up -1.0 >> out-guadalupe.txt &
# python3 kagome_solution.py -p ibm-q-ncsu/nc-state/grad-qc-class -o COBYLA -w 1.8 -i 100 >> out-guadalupe.txt &
# python3 kagome_solution.py >> out-guadalupe.txt &
dir=$HOME/vqe/solution
name=guadalupe
file=$dir/out-$name.txt

cd $dir

python3 $dir/kagome_solution.py -b ibmq_guadalupe -a ExcitationPreserving -w -1.8992 -s 2048 -q 16 >> $file &