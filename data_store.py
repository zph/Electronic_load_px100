from datetime import datetime
from os import path

from pandas import DataFrame
import pandas as pd


class DataStore:
    def __init__(self):
        self.reset()

    def __bool__(self):
        return len(self.lastrow) > 0

    def reset(self):
        self.lastrow = {}
        self.data = DataFrame()

    def append(self, row):
        print(row)
        self.lastrow = row
        self.data = pd.concat([self.data, DataFrame.from_records([row])])

    def write(self, basedir, prefix):
        filename = "{}_raw_{}.csv".format(prefix, datetime.now().strftime("%Y%m%d_%H%M%S"))
        full_path = path.join(basedir, filename)
        export_rows = self.data.drop_duplicates()
        if export_rows.shape[0]:
            print("Write RAW data to {}".format(path.relpath(full_path)))
            self.data.drop_duplicates().to_csv(full_path)
        else:
            print("no data")

    def plot(self, **args):
        return self.data.plot(**args)

    def lastval(self, key):
        return self.lastrow[key]
