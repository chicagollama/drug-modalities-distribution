#!/usr/bin/env python3

import logging
from datetime import datetime
import config as config
import os


class Log:
    def __init__(self, job):
        self.logger = logging.getLogger(__name__)
        self.job = job
        self.dir = config.results_dir
        self.file_name = f'{job}_{datetime.now().strftime("%m-%d-%Y--%H-%M-%S")}.log'
        self.file_path = os.path.join(self.dir, self.file_name)

    def get_log(self, info: str) -> str:
        logging.basicConfig(filename=self.file_path, level=logging.INFO)
        self.logger.info(info)
        print(info)
        return info

    def write_csv(self, dataset_df):
        out_file = f'{os.path.join(config.results_dir, self.job)}.csv'
        dataset_df.to_csv(out_file, index=False)
        return out_file

    @staticmethod
    def write_list_to_file(filename, datalist):
        with open(f'{filename}.txt', 'w') as outfile:
            for el in datalist:
                outfile.write(f'{el}\n')
