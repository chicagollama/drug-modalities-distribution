#!/bin/bash

mkdir ../results ../html
rm ../results/*

python3 dash-app.py
python3 dash-app-dmd.py

cd ../results ; for ilog in drug*.log moa*.log target*.log merge*.log ; do cat ${ilog} >> dmd.log ; done ; cd ..