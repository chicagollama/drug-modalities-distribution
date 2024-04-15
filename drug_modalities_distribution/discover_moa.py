#!/usr/bin/env python3

import os
import io
import pandas as pd
import json
import plotly.express as px
from collections import Counter
from common import Log
import config as config
from plotter import Plotter


# Primary keys
# ['actionType', 'chemblIds', 'mechanismOfAction', 'references', 'targetName', 'targetType', 'targets']


############################
# Parse original datasets #
############################

def parse_moa(mode="multi_target"):
    dataset = "moa"
    base_path = config.datasets_dir
    dataset_dir = 'mechanismOfAction'
    # Fields in final DataFrame
    result = ['drugId', 'targetId']

    # Initiate logger
    log = Log(job=dataset)
    info = f'\n' \
           f'{"#" * 100}\n\n' \
           f'Running discovery on {dataset.upper()} dataset\n\n' \
           f'{"#" * 100}\n\n'
    log.get_log(info=info)

    # List all .json files in folder
    json_files = sorted([ijson for ijson in os.listdir(os.path.join(base_path, dataset_dir)) if ijson.endswith(".json")])

    # Setup counters and aggregate lists
    count, taken, zero_targets, ijson = 0, 0, 0, 0
    alternative = []

    # define pandas Dataframe with the columns to get from the json
    dataset_df = pd.DataFrame(columns=result)
    info_df = pd.DataFrame(columns=['numDrugs', 'numTargets'])

    for index, js in enumerate(json_files):
        cursor = 0
        ijson += 1
        with open(os.path.join(base_path, dataset_dir, js), encoding="UTF-8") as json_file:
            for line_number, line in enumerate(json_file):
                count += 1
                cursor += 1
                print(f'json: {ijson}/{len(json_files)}, line: {cursor}, parsed items: {count}')

                line_as_file = io.StringIO(line)
                # Use a new parser for each line
                record = json.load(line_as_file)

                # Get information about drugs/targets count in entities
                numDrugs, numTargets = record["chemblIds"].__len__(), record["targets"].__len__()
                info_df.loc[count] = [numDrugs, numTargets]

                # DRUGS

                # Get [duplicates: list of drugIds for second molecules in pairs
                # they have common targets and will not get new information
                if record["chemblIds"].__len__() == 2:
                    second = record["chemblIds"][-1]
                    if second not in alternative:
                        alternative.append(second)

                # If we have 2 drugs we take only first - usually it's salt and have more target data
                drug_id = record["chemblIds"][0]

                # TARGETS
                targets = record["targets"]
                if len(targets) > 0:

                    if mode == "single_target":
                        # TODO: single target choose logic from MoA data
                        # temporary take first in list just to try
                        targets = [targets[0], ]

                    # Get final DataFrame
                    for target_id in targets:
                        taken += 1
                        dataset_df.loc[taken] = [drug_id, target_id]

                else:
                    zero_targets += 1

    # Deduplicate
    before = len(dataset_df)
    dataset_df.drop_duplicates(inplace=True)
    after_deduplicate = len(dataset_df.index)

    # Drop rows with alternative forms of drugs
    dataset_df = dataset_df[~dataset_df['drugId'].isin(alternative)]
    after_pop_alternative = len(dataset_df.index)

    # Write csv with resulting df
    out_file = log.write_csv(dataset_df=dataset_df)

    # Summary
    info = f'\n' \
           f'{count:,} items parsed\n' \
           f'{zero_targets:,} zero targets items\n' \
           f'{len(alternative):,} alternative forms (unique)\n' \
           f'{(after_deduplicate - after_pop_alternative):,} alternative forms items deleted\n' \
           f'{(before - after_deduplicate):,} duplicates deleted\n' \
           f'{after_pop_alternative:,} drug-target items saved\n' \
           f'Resulting data in {out_file}\n\n\n'

    log.get_log(info=info)

    return dataset_df, info_df


def get_info():
    # Get dataframe from initial dataset
    # my_mode = "single_target"
    dataset_df, info_df = parse_moa()

    # Get pivot
    ag = info_df.groupby('numTargets').numDrugs.value_counts().sort_index().reset_index()
    ag["numDrugs"] = ag["numDrugs"].astype(str)

    # Plot
    plotter = Plotter(job="moa")
    # MoA: drugs/targets in initial entities
    params = {"xaxis_title": "Targets per 1 entity",
              "yaxis_title": "Number of items",
              "legend_title": "Drugs per 1 entity"}

    fig = plotter.plot_scatter(idf=ag, log_y=False,
                               title="MoA: drug to target ratio in initial items")
    fig.update_layout(params)
    # fig.show()

    return fig


if __name__ == "__main__":
    get_info()
