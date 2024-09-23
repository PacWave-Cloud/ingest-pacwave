from typing import Dict, Union, Any
import numpy as np
import pandas as pd
import xarray as xr
from pydantic import BaseModel, Extra

from tsdat import DataReader


class CampbellRDIReader(DataReader):
    class Parameters(BaseModel, extra=Extra.forbid):
        read_csv_kwargs: Dict[str, Any] = {}
        from_dataframe_kwargs: Dict[str, Any] = {}

    parameters: Parameters = Parameters()

    def read(self, input_key: str) -> Union[xr.Dataset, Dict[str, xr.Dataset]]:
        data = pd.read_csv(input_key, skiprows=1, **self.parameters.read_csv_kwargs)
        data = data.drop([0, 1])

        data = data.drop(data.columns[1:6], axis=1)
        data = data.drop(data.columns[3:9], axis=1)
        data["time"] = pd.to_datetime(data["TIMESTAMP"])

        # yesterday = pd.Timestamp.now().normalize() - pd.Timedelta(days=1)
        yesterday = pd.Timestamp(
            "2022-11-08 00:00:00"
        )  # for the purpose of pipeline development
        yesterday_data_subset = data[
            data["time"].dt.normalize() == yesterday.normalize()
        ]

        ds = xr.Dataset.from_dataframe(
            yesterday_data_subset, **self.parameters.from_dataframe_kwargs
        )

        # Convert degmin.dec to deg
        latmin = ds["GPSlat"].values.astype(float)
        latdeg = latmin // 100
        ds["GPSlat"].values = latdeg + ((latdeg * 100 - latmin) / -100)

        lonmin = ds["GPSlon"].values.astype(float)
        londeg = lonmin // 100
        ds["GPSlon"].values = londeg + ((londeg * 100 - lonmin) / -100)

        return ds
