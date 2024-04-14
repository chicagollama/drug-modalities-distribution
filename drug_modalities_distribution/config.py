#!/usr/bin/env python
import os
from pathlib import Path


# Directories & files
config_dir = os.path.abspath(os.path.dirname(__file__))
project_root = Path(config_dir).parents[0]
src = config_dir
datasets_dir = os.path.join(project_root, 'datasets')
results_dir = os.path.join(project_root, 'results')
run_dir = os.path.join(project_root, 'run')
html_dir = os.path.join(project_root, 'html')
sc_file = os.path.join(datasets_dir, "subcell_uniprot.txt")

# Plotting
template="plotly_white"
# template="plotly_dark"
