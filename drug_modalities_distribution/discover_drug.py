#!/usr/bin/env python3

import os
import io
import pandas as pd
import json
import plotly.express as px
from common import Log
import config as config
from plotter import Plotter


############################
# Parse original datasets #
############################

def parse_drug():
    # temp for test
    dataset="drug"

    # Initiate logger
    log = Log(job=dataset)
    info = f'\n' \
           f'{"#" * 100}\n\n' \
           f'Running discovery on {dataset.upper()} dataset\n\n' \
           f'{"#" * 100}\n\n'
    log.get_log(info=info)

    base_path = config.datasets_dir
    dataset_dir = 'molecule'
    # Fields in final DataFrame
    result = ['drugId', 'drugName', 'drugType']

    # List all .json files in folder
    json_files = sorted([ijson for ijson in os.listdir(os.path.join(base_path, dataset_dir)) if ijson.endswith(".json")])

    # define pandas Dataframe with the columns to get from the json
    dataset_df = pd.DataFrame(columns=result)

    # run through all files/lines
    count = 0
    failed = []
    taken = []

    for index, js in enumerate(json_files):
        with open(os.path.join(base_path, dataset_dir, js), encoding="UTF-8") as json_file:
            for line_number, line in enumerate(json_file):
                count +=1
                line_as_file = io.StringIO(line)
                # Use a new parser for each line
                record = json.load(line_as_file)

                # get values
                drug_id = record['id']

                try:
                    drug_type = record['drugType']
                    # Avoid uncertainty
                    if drug_type == "unknown":
                        drug_type = "Unknown"
                    drug_name = record['name']
                    taken.append(drug_id)

                    # add to DataFrame
                    dataset_df.loc[count] = [drug_id, drug_name, drug_type]

                except KeyError:
                    print(f'\nSome keys not found! for {drug_id} in'
                          f' {json_file}: line {line_number}\n')
                    failed.append(drug_id)

    # Write csv with resulting df
    out_file = log.write_csv(dataset_df=dataset_df)

    # Summary
    info = f'\n' \
           f'{count:,} items parsed\n' \
           f'{len(taken):,} entities added\n' \
           f'{len(failed):,} failed\n' \
           f'Resulting data in {out_file}\n\n\n'

    log.get_log(info=info)

    # Write failed ids to csv file
    # if len(failed) > 0:
    #     ilog.write_list_to_file(filename=f'{dataset}_not_found', list=not_found)

    return dataset_df


def get_info():

    # Get dataframe from initial dataset
    df_drug = parse_drug()

    # Drug type distribution
    ag = df_drug.groupby("drugType", as_index=False).drugId.count()

    # Initiate Plotter class
    plotter = Plotter(job='drug')

    # Drug type distribution
    title = 'Drug modalities in starting dataset'

    # Plot histogram
    fig1 = plotter.plot_hist(idf=ag, title=f'{title}_hist')

    # Plot pie-chart
    fig2 = plotter.plot_pie_chart(idf=ag, title=f'{title}_pie')

    return fig1, fig2


if __name__ == "__main__":
    get_info()
