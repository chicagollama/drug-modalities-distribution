# DMD

## Usage

### Dash (preferable)

```python
# Directory with all scripts
cd drug_modalities_distribution
chmod +x dash-runner.sh

# Run all steps
# Provides html pages on ports 8050 & 8051
./dash-runner.sh 

# Step by step

# Extract data from datasets and get some info
# Provides html page on port 8050
python3 dash-app.py

# Analisys & visualization of merged data
# Provides html page on port 8051
python3 dash-app-dmd.py
```


### No dash

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


## TODO

### Findings
- [ ]  Add text description to figures

### Algorithmic
Optimize locations selections:
- [ ]  Weights cut-off
- [ ]  Surfaceome data

### Technical
- [ ]  Add option for DataFrame download from intermediate .csv 
- [ ]  Add download datasets to runners
- [ ]  Add tests
- [ ]  Add developer mode
- [ ]  Switch to PostgreSQL saving data vs. csv-files

### Visualization
- [ ]  Subplots for location/cluster fig10-fig11
- [ ]  Set colors on sunburst plots

