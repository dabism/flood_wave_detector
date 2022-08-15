from data_ativizig.dataloader import Dataloader
from src import PROJECT_PATH

from typing import Union
from google.cloud import storage
import os
import pandas as pd


class CombinedDataloader:
    def __init__(self):
        os.makedirs(os.path.join(PROJECT_PATH, 'data'), exist_ok=True)
        self.get_files_from_bucket()

        self.__db_credentials_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'database.ini')
        self.db = Dataloader(self.__db_credentials_path)

        self.meta = self.get_metadata()
        self.pre_data = self.create_pre_data()

    def get_files_from_bucket(self):
        """Downloads a blob from the bucket."""
        storage_client = storage.Client()
        origin_bucket = storage_client.bucket("ativizig-phase-3")

        src_data = "fwd-data-1951-pre-edited/data-and-meta/fwd-data-edited_1876_1950.csv"
        pre_data = origin_bucket.blob(src_data)

        dest_data = os.path.join(PROJECT_PATH, 'data', 'data_pre_1951.csv')
        pre_data.download_to_filename(dest_data)
        self.log(src_data, "ativizig-phase-3", dest_data)
        # TODO: Add meta data download

    def create_pre_data(self):
        raw_data = pd.read_csv(os.path.join(PROJECT_PATH, 'data', 'data_pre_1951.csv'), index_col=[0])[: -1]

        reg_name_pairs = self.meta['station_name'].to_dict()
        reg_name_pairs = dict((v, k) for k, v in reg_name_pairs.items())

        pre_data = raw_data.rename(columns=reg_name_pairs)
        pre_data.index = pd.to_datetime(pre_data.index)
        return pre_data

    def get_daily_time_series(self, reg_number_list: list, threshold: Union[None, int] = None):
        pro_data = self.db.get_daily_time_series(reg_number_list=reg_number_list, threshold=threshold)
        # TODO: Check if given stations are available in the database (1951 and after)
        pre_reg_list = [reg for reg in reg_number_list if reg in self.pre_data]
        pre_data = self.pre_data[pre_reg_list]
        pre_data.columns = pre_data.columns.astype(str)
        return pd.concat([pre_data, pro_data])

    def get_metadata(self):
        meta = self.db.meta_data \
                    .groupby(["river"]) \
                    .get_group("Tisza") \
                    .sort_values(by='river_km', ascending=False)

        # TODO: Merge with new meta table
        return meta

    @staticmethod
    def log(source: str, bucket: str, destination: Union[str, bytes]):
        print(f"Downloaded storage object {source} from bucket {bucket} to local file {destination}.")


if __name__ == "__main__":
    comb_dataloader = CombinedDataloader()
    data = comb_dataloader.get_daily_time_series(reg_number_list=[2541, 1514, 1515])
