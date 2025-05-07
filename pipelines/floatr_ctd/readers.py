from typing import Dict, Union, Any
from pydantic import BaseModel, Extra
import numpy as np
import pandas as pd
import xarray as xr
from datetime import datetime, time as dtime
from mhkit.dolfyn.time import date2dt64
from tsdat import DataReader


class SeabirdCTDReader(DataReader):
    """---------------------------------------------------------------------------------
    Reader for Seabird CTD dat files sent from the FLOATr buoy to the OSU server.
    ---------------------------------------------------------------------------------"""

    class Parameters(BaseModel, extra=Extra.forbid):
        read_csv_kwargs: Dict[str, Any] = {}
        from_dataframe_kwargs: Dict[str, Any] = {}

    parameters: Parameters = Parameters()

    def old_header(self, input_key):
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

        return df

    def new_header(self, input_key):
        df = pd.read_csv(
            input_key, header=0, skiprows=1, **self.parameters.read_csv_kwargs
        )
        df = df.drop([0, 1])

        df["time"] = pd.to_datetime(df["TIMESTAMP"])

        return df

    def read(self, input_key: str) -> Union[xr.Dataset, Dict[str, xr.Dataset]]:
        # Read csv file

        df = self.old_header(input_key)
        if not df.dropna().size:
            try:
                df = self.new_header(input_key)
            except:
                raise EOFError("No data found in file.")

        # Use correct names
        df["temp"] = df["scat(1)"]
        df["conductivity"] = df["scat(2)"]
        df["do"] = df["scat(3)"]
        df["salinity"] = df["scat(5)"]

        ds = xr.Dataset.from_dataframe(df, **self.parameters.from_dataframe_kwargs)

        return ds
