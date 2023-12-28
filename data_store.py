from datetime import datetime
from os import path
import json

from pandas import DataFrame
import pandas as pd

import logging
from settings import get_settings

log = logging.getLogger(__name__)



class DataStore:
    def __init__(self):
        self.reset()

    def __bool__(self):
        return len(self.lastrow) > 0

    def reset(self):
        self.lastrow = {}
        self.data = DataFrame()

    def append(self, row):
        row["ts"] = datetime.now()
        row_json = json.dumps(row, default=str)
        log.info(f"ROW: {row_json}")

        with open(f"""{get_settings()["cell_label"]}.jsonl""", "a") as f:
            f.write(row_json)
            f.write("\n")

        self.lastrow = row
        self.data = pd.concat([self.data, DataFrame.from_records([row])])

    def write(self, basedir, prefix):
        filename = "{}_raw_{}.csv".format(prefix, datetime.now().strftime("%Y%m%d_%H%M%S"))
        full_path = path.join(basedir, filename)
        export_rows = self.data.drop_duplicates()
        if export_rows.shape[0]:
            log.debug("Write RAW data to {}".format(path.relpath(full_path)))
            self.data.drop_duplicates().to_csv(full_path)
        else:
            log.debug("no data")

    def plot(self, **args):
        return self.data.plot(**args)

    def lastval(self, key):
        return self.lastrow[key]
