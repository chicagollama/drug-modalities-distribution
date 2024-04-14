#!/usr/bin/env python3

import os
import pandas as pd
from subcellular_parse import SubcellularUniprot
import config as config
import plotter as plotter
from common import Log


###############
# GET DATA
###############
work_path = config.results_dir
merge_csv = os.path.join(work_path, "merged.csv")
df = pd.read_csv(merge_csv)

unique_locations = list(set(df.targetLocation.tolist()))

# Get subcellular notations
sc = SubcellularUniprot()


###############
# GROUP & PLOT
###############

# Initiate logger
log = Log(job="merged2plot")

info = f'\n' \
       f'{"#" * 100}\n\n' \
       f'Plotting merged DMD data!\n\n' \
       f'{"#" * 100}\n\n' \
       f'Got dataframe of {len(df.index)} rows' \
       f'Resulting htmls in {config.html_dir}\n\n\n' \

log.get_log(info=info)


###############
# COMMON LOCS
###############

# Group: targetLocationName | drugType
locs_drugcount = df.groupby('targetLocationName').drugType.value_counts().sort_index().reset_index()
locs_drugcount.columns = ['targetLocationName', 'drugType', 'drugCount']

# All locations | all drug modalities
fig = plotter.plot_scatter(idf=locs_drugcount, title="All locations | all drug modalities")

###############
# CLUSTERS
###############

# Group: targetLocationCluster | drugType
clusters_drugcount = df.groupby('targetLocationCluster').drugType.value_counts().sort_index().reset_index()
clusters_drugcount.columns = ['targetLocationCluster', 'drugType', 'drugCount']
plotter.plot_scatter(idf=clusters_drugcount, title="Clusters | drug modalities")

# Clusters counted for all locations without reduction
# Group: targetLocationCluster | drugId
all_clusters = df.groupby('targetLocationCluster', as_index=False).drugId.count()
plotter.plot_pie_chart(idf=all_clusters, title="Clusters counted for all locations without reduction")

# Group: targetLocationCluster | targetLocationName
double_drugcount = df.groupby(['targetLocationCluster', 'targetLocationName']).drugType.value_counts().reset_index()

plotter.plot_sunbirst(double_drugcount, title='Clusters | locations | all drugs', path=['targetLocationCluster', 'targetLocationName'])
plotter.plot_sunbirst(double_drugcount, title='Clusters | drug modality | all drugs', path=['targetLocationCluster', 'drugType'])


###############
# MLP
###############

# Group by locations
mlp_all_df = df.groupby('drugId', as_index=False).targetLocationName.count()
mlp_all_df.columns = ['drugId', 'locationCount']

# Group by locations count
double_mlp = mlp_all_df.groupby('locationCount', as_index=False).drugId.count()

# Multiple locations per drug
plotter.plot_hist(idf=double_mlp, title="MLP | All drugs", nbins=300)

###### Get MLP as column ######

# Label all for location count & MLP flag
# Add location count and get MLP status for all drugs
df_with_mlp = pd.merge(df, mlp_all_df, on = "drugId")
df_with_mlp["multipleLocations"] = df_with_mlp.apply(lambda row: "ML" if row.locationCount > 1 else "SL", axis=1)

# Group by MLP | targetLocationName
loc_mlp = df_with_mlp.groupby('targetLocationName').multipleLocations.value_counts().reset_index()

# Distribution of ML on targetLocations !!!!!!!
plotter.plot_sunbirst(loc_mlp, title='Locations | MLP', path=['multipleLocations', 'targetLocationName'])


###############
# REDUCE LOCATIONS DIVERSITY
# TO CLUSTERS DISTRIBUTION
# MAYBE IT'LL DELETE MOST MLPS
###############

# Get clusters count
# Group by drugId | targetLocationCluster
clust_count = df.groupby('drugId').targetLocationCluster.value_counts().reset_index()

# Group by drugId | clusterCount
clust_double_count = clust_count.groupby('drugId').targetLocationCluster.count().reset_index()

# Circle for Clusters | All drugs
clusters_all_relative = clust_count.groupby('targetLocationCluster').drugId.count().reset_index()
plotter.plot_pie_chart(idf=clusters_all_relative, title="Clusters distribution | All drugs | Locations reduced to clusters")

######## Compare to non-reduced:
# > Clusters counted for all locations without reduction
plotter.plot_pie_chart(idf=all_clusters, title="Clusters counted for all locations without reduction")
######## Result: Reduced clusters are more balanced

###############
# IT DID
###############

###############
# AVARAGE CLUSTER
###############

###################
# CLUSTERS REGISTRY
###################
clust_dict = clust_count.groupby('drugId')[['targetLocationCluster','count']].apply(lambda g: list(map(tuple, g.values.tolist()))).to_dict()
# {'CHEMBL4594472': [('Cytoplasm', 6), ('Nucleus', 4), ('Surface', 3), ('Secreted', 2)],}

# Add average cluster to df as column
df["singleClust"] = df.apply(lambda row: sc.main_cluster(iclust_dict=dict(clust_dict[row.drugId])), axis=1)

# Group by singleCluster | drugType
aav_clust = df.groupby(['drugId', 'singleClust']).drugType.value_counts().reset_index()
av_clust = aav_clust.drop(['count'], axis=1)
clust_modality = av_clust.groupby('singleClust').drugType.value_counts().reset_index()

# Average cluster | drug modality
plotter.plot_sunbirst(clust_modality, title='Average cluster | drug modality | all drugs', path=['singleClust', 'drugType'])

######################
# AB | SM | PR -> Cluster || single cluster mode
######################

# Discover the most crowded modalities: Small molecule & Antibody & Protein
def get_dfs():
    dfs = []
    for itype in ('Antibody', 'Small molecule', 'Protein'):
        modality_avclust = av_clust[av_clust.drugType == itype].reset_index()
        plot_modality_avclust = modality_avclust.groupby('singleClust').drugId.count().reset_index()
        plotter.plot_pie_chart(plot_modality_avclust, title=f'Average cluster | {itype}')
        dfs.append(plot_modality_avclust.to_dict())
    return dfs

# TODO: Plot as subplots
# plotter.subplots_pie_chart(title='K', dfs=get_dfs(), subtitles=(1,2,3))

######################
# Clusters -> drug modality || single cluster mode
######################
for iclust in sc.global_locs().keys():
    cluster_avclust = av_clust[av_clust.singleClust == iclust].reset_index()
    plot_cluster_avclust = cluster_avclust.groupby('drugType').drugId.count().reset_index()
    plotter.plot_pie_chart(plot_cluster_avclust, title=f'Average cluster | {iclust}')

# TODO: Plot as subplots

###############
# ADC CHECK
###############

# Seems like there some anomality in Antibody's locations/clusters
# Though they can't got into the cell
# How can they be so much linked to Cytoplasm proteins?

print("CHECK FOR ADC")
# Take AB with single cluster Cytoplasm | Nucleus
# It's not strict check, but a hint: ADCs usually have name like 'LIFASTUZUMAB VEDOTIN'

for iclust in ('Nucleus', 'Cytoplasm'):
    adc_check = df[(df.drugType == 'Antibody') & (df.singleClust == iclust)].reset_index()
    names = list(set(list(adc_check.drugName)))
    adcs = [i for i in names if ' ' in i]
    print(f'{len(adcs)} ADC from {len(names)} for {iclust}')

###############
# Well, not so much :(
###############
# 6 ADC from 41 for Nucleus
# 40 ADC from 218 for Cytoplasm

