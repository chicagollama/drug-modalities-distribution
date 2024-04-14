# DMD

## Usage

```python
# Directory with all scripts
cd drug_modalities_distribution
chmod +x runner.sh

# Run all steps
./runner.sh 

# Step by step

# Extract data from MOLECULE dataset and get some info
discover_drug.py

# Extract data from MOA dataset and get some info
discover_mao.py

# Extract data from TARGET dataset and get some info
discover_targets.py

# Combine data from all datasets to LINK drug modality to target location
merge.py

# Analisys & visualization of merged data, provides multiple plots
merged2plot.py
```
## Data

Datasets must be located at datasets directory unpacked. 

Datasets used: Target, Drug, Drug - mechanism of action; Subcellular from Uniprot (already stored). 

All intermediate data is stored at result dir as .csv files.

