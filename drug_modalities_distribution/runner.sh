#!/bin/bash

rm ../results/*

python3 discover_drug.py
python3 discover_moa.py
python3 discover_target.py
python3 merge.py
python3 merged2plot.py

cd ../results ; for ilog in drug*.log moa*.log target*.log merge*.log ; do cat ${ilog} >> dmd.log ; done ; cd ..