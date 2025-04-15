import json
from typing import Any, Dict, Union
from pydantic import BaseModel, Extra
from pathlib import Path
import numpy as np
import xarray as xr
from tsdat import DataReader


class NexsensJsonReader(DataReader):
    """Reads Sofar Spotter json data downloaded through the Sofar API interface."""

    class Parameters(BaseModel, extra=Extra.forbid):

        read_csv_kwargs: Dict[str, Any] = {}
        from_dataframe_kwargs: Dict[str, Any] = {}

    parameters: Parameters = Parameters()

    def read(self, input_key: str) -> Union[xr.Dataset, Dict[str, xr.Dataset]]:
        # Request requires that nexsens belongs to the user (token)
        # API_KEY = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"  # Your NexSens API Key
        # DEVICE_ID = "4177"  # Device ID for X3-SUB-4G-20010
        # url = f"https://www.wqdatalive.com/api/v1/devices/{DEVICE_ID}/parameters/data/latest?apiKey={API_KEY}"
        # res = requests.get(url)
        # data = res.json()
        # with open("data.json", "w") as f:
        #     json.dump(data, f)

        # Open retrieved data
        f = open(input_key)
        data = json.load(f)

        if not data["data"]:
            raise EOFError("No data recorded.")

        ds_dict = {}
        for row in data["data"]:
            ds_dict[row["name"]] = {
                "dims": (),
                "data": np.array(row["value"]).astype(float),
                # "attrs": {"units": row["unit"], "id": row["id"]},
            }
        ds = xr.Dataset.from_dict(ds_dict)
        ds = ds.assign_coords(
            {"time": np.array(row["timestamp"], dtype="datetime64[ns]")}
        )
        ds.attrs["nexsens_id"] = Path(input_key).stem.split(".")[0]

        return ds
