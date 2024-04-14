#!/usr/bin/env python3

import os
import io
import pandas as pd
import json
import plotly.express as px
from collections import Counter

from subcellular_parse import SubcellularUniprot
import config as config
from common import Log


# Target primary keys
tar_prim_keys = ['approvedName', 'approvedSymbol', 'biotype', 'canonicalExons',
                 'canonicalTranscript', 'constraint', 'dbXrefs',
                 'functionDescriptions', 'genomicLocation', 'go', 'homologues',
                 'id', 'nameSynonyms', 'obsoleteNames', 'obsoleteSymbols',
                 'pathways', 'proteinIds', 'subcellularLocations',
                 'symbolSynonyms', 'synonyms', 'targetClass', 'tractability',
                 'transcriptIds']


# Get SC code2name dict

sc = SubcellularUniprot()

############################
# Parse original dataset   #
############################


def parse_targets():
    """" Parse json files with datasets to pandas DataFrame"""
    dataset = "target"
    print(f'Running discovery on {dataset.upper()} dataset\n\n')

    # Initiate logger
    log = Log(job=dataset)
    info=f'\n' \
         f'{"#" * 100}\n\n' \
         f'Running discovery on {dataset.upper()} dataset\n\n' \
         f'{"#" * 100}\n\n'
    log.get_log(info=info)

    base_path = config.datasets_dir
    dataset_dir = "targets"
    # Fields in final DataFrame
    result = ['targetId', 'targetLocation', 'targetLocationName', 'targetLocationCluster']

    # List all .json files in folder
    json_files = sorted([ijson for ijson in os.listdir(os.path.join(base_path, dataset_dir)) if ijson.endswith(".json")])

    # Setup counters and aggregate lists
    count = 0
    zero_locs = []
    zero_locs_biotypes = []
    non_zero_locs_biotypes = []
    locations = []
    count_targets = 0
    count_locs = 0
    not_standart = []
    locs_without_sl_code = 0
    ijson = 0

    # Define pandas Dataframe with the columns to get from the json
    dataset_df = pd.DataFrame(columns=result)

    # Information about source data
    info_df = pd.DataFrame(columns=['targetId', 'numLocations'])

    # Iterate through all entities in all json files
    for index, js in enumerate(json_files):
        ijson += 1
        cursor = 0
        with open(os.path.join(base_path, dataset_dir, js), encoding="UTF-8") as json_file:
            for line_number, line in enumerate(json_file):
                count +=1
                cursor += 1
                print(f'json: {ijson}/{len(json_files)}, line: {cursor}, total parsed items: {count}')

                line_as_file = io.StringIO(line)
                # Use a new parser for each line
                record = json.load(line_as_file)

                # Main key
                target_id = record['id']

                # Check number of locations:
                if 'subcellularLocations' in record.keys():
                    num_locations = record['subcellularLocations'].__len__()

                    # Explore non-zero locations
                    if num_locations > 0:
                        # Keep info for common description of dataset
                        non_zero_locs_biotypes.append(record['biotype'])
                        info_df.loc[count] = [target_id, num_locations]

                        # Get all "non-standart" locations: not in Subcellular Uniprot codes
                        #TODO: do we need this information?
                        loc_names = [el['location'] for el in record['subcellularLocations'] if 'location' in el.keys()]
                        for i in loc_names:
                            if i != '':
                                # Delete Isoform data in location field like '[Isoform p56]: Nucleus'
                                i = i.split(":")[-1].strip()
                                if i not in sc.code_name_dict().values():
                                    if i not in not_standart:
                                        not_standart.append(i)

                        # SL codes for all locations from "Term_SL" field
                        # TODO: Run on Uniprot source only
                        terms = []
                        for item in record['subcellularLocations']:
                            if "source" in item.keys():
                                if item["source"] == "uniprot":
                                    if 'termSL' in item.keys():
                                        terms.append(item['termSL'])

                                    # Try to get location if there is no "TermSL" data
                                    else:
                                        locs_without_sl_code += 1
                                        # Clean Isoform or other variant data from field "location"
                                        iloc = item['location'].split(":")[-1].strip()
                                        try_sl_code = sc.translate(iloc)
                                        if try_sl_code:
                                            print(f"! Got SL from location yet Term_SL is empty! {target_id}: {try_sl_code}")
                                            # Add to all terms
                                            terms.append(try_sl_code)
                                            # TODO: delete, will get from DataFrame
                                            locations.append(try_sl_code)
                                        else:
                                            if iloc not in not_standart:
                                                not_standart.append(iloc)

                        # Keep only unique locations
                        terms = list(set(terms))
                        #TODO: delete, will get from DataFrame
                        locations.extend(terms)

                        # Now let's put data to final DataFrame
                        if len(terms) > 0:
                            count_targets += 1
                            for iterm in terms:
                                count_locs += 1
                                dataset_df.loc[count_locs] = [record['id'], iterm, sc.translate(iterm), sc.get_cluster(iterm)]

                    else:
                        zero_locs.append(record['id'])
                        zero_locs_biotypes.append(record['biotype'])
                else:
                    # Keep info about zero locations
                    zero_locs.append(record['id'])
                    zero_locs_biotypes.append(record['biotype'])

    # Write csv with resulting df
    out_file = log.write_csv(dataset_df=dataset_df)

    # Summary
    info = f'\n' \
           f'{count:,} total\n' \
           f'{locs_without_sl_code:,} locations subitems has no LS Uniprot code\n' \
           f'{len(zero_locs_biotypes):,} zero locations\n' \
           f'{count_targets:,} targets with locations\n' \
           f'{count_locs:,} locations including multiple\n' \
           f'Resulting data in {out_file}\n\n\n'

    log.get_log(info=info)

    # Keep several data counters for illustartions
    # TODO: Illustrate in place? Replace Counter for another DataFrame?

    locations_counter = dict(Counter(sc.translate(loc) for loc in locations))
    # locations_df = pd.DataFrame(dict(biotype=[code2name[key] for key in locations_counter.keys()], numTargets=locations_counter.values()))

    zero_counter = dict(Counter(zero_locs_biotypes))
    # zero_df = pd.DataFrame(dict(biotype=zero_counter.keys(), numTargets=zero_counter.values()))

    non_zero_counter = dict(Counter(non_zero_locs_biotypes))
    # non_zero_df = pd.DataFrame(dict(biotype=non_zero_counter.keys(), numTargets=non_zero_counter.values()))

    return info_df, dataset_df, zero_counter, non_zero_counter, locations_counter


########
# RUN
########

# Get all data
info_df, dataset_df, zero_counter, non_zero_counter, locations_counter = parse_targets()


########
# PLOT
########

# TODO: plot using Plotter class from plotter.py

def histo_for_counter(counter: dict, title: str, x_title: str) -> None:
    """ Get distribution by categories in list"""
    # Turn to pandas dataframe
    df = pd.DataFrame(dict(categories=counter.keys(), count=counter.values()))
    # create figure
    hb_fig = px.histogram(df, x='categories', y='count')
    hb_fig.layout.template = "plotly_dark"
    hb_fig.update_layout(
            title=title,
            xaxis_title=x_title,
            yaxis_title='count',
            font=dict(size=20)
    )
    hb_fig.update_xaxes(categoryorder='total descending')
    hb_fig.show()


# Starting dataset

# All locations distribution
histo_for_counter(counter=locations_counter, title="All target Locations", x_title="location")

# Zero location
histo_for_counter(counter=zero_counter, title="Targets without locations", x_title="biotype")

# Non-zero location
histo_for_counter(counter=non_zero_counter, title="Targets with locations", x_title="biotype")

# Number of locations per target
fig = px.histogram(info_df, x='numLocations')
fig.layout.template = "plotly_dark"
fig.update_layout(
        title="Targets with locations data",
        xaxis_title="number of locations per target",
        yaxis_title="targets count",
        font=dict(size=20),
        bargap=0.2, # gap between bars of adjacent location coordinates
        xaxis=dict(tickmode='linear')
)
fig.show()


# Resulting dataset (data taken)

# Get pivot
ag = dataset_df.groupby("targetLocationName", as_index=False).targetId.count()

# Pie-chart for locations
fig2 = px.pie(ag, values='targetId', names='targetLocationName', title='Locations distribution in target dataset')
fig2.update_layout(
    font=dict(size=20),
    template = "plotly_dark"
)
fig2.update_traces(textinfo='none')
fig2.show()
