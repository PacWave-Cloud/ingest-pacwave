from typing import Dict, Union, Any
from pydantic import BaseModel, Extra
import numpy as np
import pandas as pd
import xarray as xr
from datetime import datetime, time as dtime
from mhkit.dolfyn.time import date2dt64
from tsdat import DataReader


class SeabirdCTDReaderV2(DataReader):
    """---------------------------------------------------------------------------------
    Reader for Seabird CTD df files sent from the FLOATr buoy to the OSU server.
    ---------------------------------------------------------------------------------"""

    class Parameters(BaseModel, extra=Extra.forbid):
        read_csv_kwargs: Dict[str, Any] = {}
        from_dataframe_kwargs: Dict[str, Any] = {}

    parameters: Parameters = Parameters()

    def read(self, input_key: str) -> Union[xr.Dataset, Dict[str, xr.Dataset]]:
        df = pd.read_csv(
            input_key, header=0, skiprows=1, **self.parameters.read_csv_kwargs
        )
        df = df.drop([0, 1])

        df["time"] = pd.to_datetime(df["TIMESTAMP"])

        # Use correct names
        df["temp"] = df["scat(1)"]
        df["conductivity"] = df["scat(2)"]
        df["do"] = df["scat(3)"]
        df["salinity"] = df["scat(5)"]

        ds = xr.Dataset.from_dataframe(df, **self.parameters.from_dataframe_kwargs)

        return ds


class SeabirdCTDReaderV1(DataReader):
    """---------------------------------------------------------------------------------
    Reader for Seabird CTD df files sent from the FLOATr buoy to the OSU server.
    ---------------------------------------------------------------------------------"""

    class Parameters(BaseModel, extra=Extra.forbid):
        read_csv_kwargs: Dict[str, Any] = {}
        from_dataframe_kwargs: Dict[str, Any] = {}

    parameters: Parameters = Parameters()

    def read(self, input_key: str) -> Union[xr.Dataset, Dict[str, xr.Dataset]]:
        names = [
            "LOGGER ID",
            "YEAR",
            "JULIAN DAY",
            "HHMM",
            "ERROR",
            "scat(1)",
            "scat(2)",
            "scat(3)",
            "scat(4)",
            "scat(5)",
        ]
        df = pd.read_csv(
            input_key,
            header=None,
            names=names,
            na_values=-7999,
            **self.parameters.read_csv_kwargs,
        )
        # Drop entries where all values are missing - timestamps can get repeated
        data_list = ["scat(1)", "scat(2)", "scat(3)", "scat(4)", "scat(5)"]
        mask = df[data_list].notna().all(axis=1)
        df = df[mask]

        # Make time coordinate
        coord = []
        for i, row in df.iterrows():
            datestring = f"{int(row['YEAR'])}{int(row['JULIAN DAY'])}"
            date = datetime.strptime(datestring, "%Y%j")

            hour = str(int(row["HHMM"])).zfill(4)[:2]
            minute = str(int(row["HHMM"])).zfill(4)[2:]
            time = dtime(int(hour), int(minute), 0)
            coord.append(datetime.combine(date, time))

        df["time"] = date2dt64(coord)
        df = df.drop(columns=["YEAR", "JULIAN DAY", "HHMM", "ERROR"])

        # Use correct names
        df["temp"] = df["scat(1)"]
        df["conductivity"] = df["scat(2)"]
        df["do"] = df["scat(3)"]
        df["salinity"] = df["scat(5)"]

        ds = xr.Dataset.from_dataframe(df, **self.parameters.from_dataframe_kwargs)

        return ds
