#!/usr/bin/env python3

import os
import io
import pandas as pd
import config as config
from common import Log


def get_merged():
       # Run extraction for each ds

       # Prepared subsets in csv files
       csv_path = config.results_dir

       # drug
       infile = os.path.join(csv_path, f'drug.csv')
       df_drug = pd.read_csv(infile)


       # moa
       infile = os.path.join(csv_path, f'moa.csv')
       df_moa = pd.read_csv(infile)


       # target
       infile = os.path.join(csv_path, f'target.csv')
       df_target = pd.read_csv(infile)
       # df_target = df_target.drop_duplicates()


       # Get merged table
       # Merge molecule and moa
       merge_drug_to_moa = pd.merge(df_drug, df_moa, on="drugId")

       # Merge result with target
       merge_molecule_to_moa_to_target = pd.merge(merge_drug_to_moa, df_target, how="inner", on="targetId")
       buf = io.StringIO()
       merge_molecule_to_moa_to_target.info(buf=buf)
       df_info = buf.getvalue()

       # Write merged to csv
       out_file = f'{os.path.join(config.results_dir, "merged")}.csv'
       merge_molecule_to_moa_to_target.to_csv(out_file, index=False)

       # Show and log Summary info
       # Initiate logger
       log = Log(job='merge')

       info = f'\n' \
              f'{"#" * 100}\n\n' \
              f'MERGED datasets to DMD!\n\n' \
              f'{"#" * 100}\n\n' \
              f'Resulting data in {out_file}\n\n' \
              f'Summary dataset info:\n' \
              f'{df_info}\n\n\n'

       log.get_log(info=info)

       return info


if __name__ == "__main__":
       get_merged()
