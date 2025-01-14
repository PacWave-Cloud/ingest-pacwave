from typing import Dict, Union, Any
import numpy as np
import pandas as pd
import xarray as xr
from pydantic import BaseModel, Extra

from tsdat import DataReader


class SeabirdCTDReader(DataReader):
    """---------------------------------------------------------------------------------
    Reader for Seabird CTD csv files sent from the FLOATr buoy to the OSU server.
    ---------------------------------------------------------------------------------"""

    class Parameters(BaseModel, extra=Extra.forbid):
        read_csv_kwargs: Dict[str, Any] = {}
        from_dataframe_kwargs: Dict[str, Any] = {}

    parameters: Parameters = Parameters()

    def read(self, input_key: str) -> Union[xr.Dataset, Dict[str, xr.Dataset]]:
        df = pd.read_csv(input_key, **self.parameters.read_csv_kwargs)
        df = df.drop([0, 1])

        df["time"] = pd.to_datetime(df["TIMESTAMP"])

        # Use correct names
        df["temp"] = df["scat(1)"]
        df["conductivity"] = df["scat(2)"]
        df["do"] = df["scat(3)"]
        df["salinity"] = df["scat(5)"]

        ds = xr.Dataset.from_dataframe(df, **self.parameters.from_dataframe_kwargs)

        return ds
