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
from plotter import Plotter


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
    locations = []
    count_targets = 0
    count_locs = 0
    not_standart = []
    locs_without_sl_code = 0
    ijson = 0

    # Define pandas Dataframe with the columns to get from the json
    dataset_df = pd.DataFrame(columns=result)

    # Information about source data
    info_df = pd.DataFrame(columns=['targetId', 'targetBiotype', 'numLocations'])

    # Iterate through all entities in all json files
    for index, js in enumerate(json_files):
        ijson += 1
        cursor = 0
        with open(os.path.join(base_path, dataset_dir, js), encoding="UTF-8") as json_file:
            for line_number, line in enumerate(json_file):
                count += 1
                cursor += 1
                print(f'json: {ijson}/{len(json_files)}, line: {cursor}, total parsed items: {count}')

                line_as_file = io.StringIO(line)
                # Use a new parser for each line
                record = json.load(line_as_file)

                # Main key
                target_id = record['id']
                target_biotype = record['biotype']
                if record['biotype'] == '':
                    target_biotype = 'NA'

                # Check number of locations:
                if 'subcellularLocations' in record.keys():
                    num_locations = record['subcellularLocations'].__len__()

                    # Explore non-zero locations
                    if num_locations > 0:
                        # Keep info for common description of dataset
                        info_df.loc[count] = [target_id, target_biotype, num_locations]

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
                        info_df.loc[count] = [target_id, target_biotype, num_locations]
                else:
                    # Keep info about zero locations
                    info_df.loc[count] = [target_id, target_biotype, 0]

    # Write csv with resulting df
    out_file = log.write_csv(dataset_df=dataset_df)

    # Summary
    info = f'\n' \
           f'{count:,} total\n' \
           f'{locs_without_sl_code:,} locations subitems has no LS Uniprot code\n' \
           f'{count_targets:,} targets with locations\n' \
           f'{count_locs:,} locations including multiple\n' \
           f'Resulting data in {out_file}\n\n\n'

    log.get_log(info=info)

    # Keep several data counters for illustartions
    # TODO: Illustrate in place? Replace Counter for another DataFrame?

    locations_counter = dict(Counter(sc.translate(loc) for loc in locations))
    # locations_df = pd.DataFrame(dict(biotype=[code2name[key] for key in locations_counter.keys()], numTargets=locations_counter.values()))

    return info_df, dataset_df, locations_counter


def get_info():
    ########
    # RUN
    ########

    # Get all data
    info_df, dataset_df, locations_counter = parse_targets()


    #################
    # BIOTYPE
    #################

    biotype_nlocs = info_df.groupby(["targetBiotype", "numLocations"]).targetId.count().reset_index()

    # Get plotter
    plotter = Plotter(job="target")

    # Plot zero-location / biotype distribution
    zero = biotype_nlocs[biotype_nlocs.numLocations == 0]
    fig1 = plotter.plot_hist(idf=zero, title="Targets dataset: Targets with zero locations")

    # Plot nonzero-location / biotype distribution
    non_zero = biotype_nlocs[biotype_nlocs.numLocations > 0]
    # TODO: add single bar coloring for "protein_coding" (color_discrete_map={"protein_coding": "red"})
    fig2 = plotter.plot_hist(idf=non_zero, title="Targets dataset: Targets with non-zero locations")

    #################
    # LOCATIONS COUNT
    #################

    # Plot locations distribution
    locations = info_df.groupby("numLocations").targetId.count().reset_index()
    fig3 = plotter.plot_hist(idf=locations, title="Targets dataset: Locations count distribution", nbins=max(list(info_df.numLocations))+1)

    locations_df = pd.DataFrame(dict(categories=locations_counter.keys(), count=locations_counter.values()))
    fig4 = plotter.plot_hist(idf=locations_df, title="Targets dataset: Locations distribution hist")
    fig5 = plotter.plot_pie_chart(idf=locations_df,
                                  title="Targets dataset: Locations distribution",
                                  color_map="cluster")

    return fig1, fig2, fig3, fig4, fig5


if __name__ == "__main__":
    get_info()
