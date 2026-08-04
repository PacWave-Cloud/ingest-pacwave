import json
from typing import Any, Dict, Union
from pydantic import BaseModel
from pathlib import Path
import numpy as np
import xarray as xr
from tsdat import DataReader


class NexsensJsonReader(DataReader):
    """Reads Nexsens json data downloaded through the WQ Data interface."""

    class Parameters(BaseModel):

        read_csv_kwargs: Dict[str, Any] = {}
        from_dataframe_kwargs: Dict[str, Any] = {}

    parameters: Parameters = Parameters()

    def read(self, input_key: str) -> Union[xr.Dataset, Dict[str, xr.Dataset]]:
        data = json.load(open(input_key))

        if not data["data"]:
            raise EOFError("No data recorded.")

        ds_dict = {}
        timestamps = []
        for row in data["data"]:
            timestamps.append(row["timestamp"])
            # Probably a better way to do this, but here we are.
            for item in row["values"]:
                pid = str(item["parameterId"])
                if pid not in ds_dict:
                    ds_dict[pid] = {
                        "dims": ("time"),
                        "data": np.array(item["value"]).astype(float),
                    }
                else:
                    ds_dict[pid].update(
                        {
                            "data": np.append(
                                ds_dict[pid]["data"],
                                np.array(item["value"]).astype(float),
                            )
                        }
                    )

        ds = xr.Dataset.from_dict(ds_dict)
        ds = ds.assign_coords({"time": np.array(timestamps, dtype="datetime64[ns]")})
        ds.attrs["nexsens_id"] = Path(input_key).stem.split(".")[0]

        return ds
