import json
import numpy as np
import pandas as pd
import xarray as xr
from typing import Any, Dict, Union
from pydantic import BaseModel, Extra
from tsdat import DataReader
from mhkit.dolfyn import time


class SpotterCSVReader(DataReader):
    """Reads Sofar Spotter CSV data downloaded from the Spotter online dashboard."""

    class Parameters(BaseModel, extra=Extra.forbid):

        read_csv_kwargs: Dict[str, Any] = {}
        from_dataframe_kwargs: Dict[str, Any] = {}

    parameters: Parameters = Parameters()

    def read(self, input_key: str) -> Union[xr.Dataset, Dict[str, xr.Dataset]]:
        # Read csv file with pandas
        df = pd.read_csv(input_key, **self.parameters.read_csv_kwargs)
        # Convert missing data (-) to nan
        df = df.replace("-", np.nan)
        # Set index
        df["timestamp"] = time.epoch2dt64(df["Epoch Time"])
        df = df.drop("Epoch Time", axis=1)
        df.index = df["timestamp"]

        # Find length of frequency vector
        col_names = df.columns.to_list()
        i = 0
        while f"f_{i}" in col_names:
            i += 1

        # Compress row of variables in input into variables dimensioned by time and height
        raw_categories = [
            "f",
            "df",
            "a1",
            "b1",
            "a2",
            "b2",
            "varianceDensity",
            "direction",
            "directionalSpread",
        ]
        output_var_names = [
            "frequency",
            "deltaFrequency",
            "a1",
            "b1",
            "a2",
            "b2",
            "psd",
            "theta",
            "phi",
        ]

        dataset = xr.Dataset()
        for category, output_name in zip(raw_categories, output_var_names):
            var_names = [f"{category}_{x}" for x in range(i)]
            # Collate 2D variable pieces into one list
            var_data = [df[name].dropna() for name in var_names]
            # Convert list of series to dataframe and sort time index properly
            df_var = pd.DataFrame(var_data).T.sort_index()
            # Save into dataset
            dataset[output_name] = xr.DataArray(
                df_var.astype("float32").values,
                coords={"timestamp": df_var.index, "index": range(df_var.shape[-1])},
            )
            for name in var_names:
                df = df.drop(name, axis=1)

        # Drop nan rows after removing spectral variables and sort time index properly
        df = df.dropna().sort_index()

        # Frequency vector shouldn't change with time
        if len(np.unique(dataset.frequency).shape) > 1:
            assert ValueError("Multiple frequency vectors detected")

        dataset["frequency"] = dataset["frequency"][0]

        dataset = xr.merge((df.to_xarray(), dataset))

        return dataset


class SpotterJsonReader(DataReader):
    """Reads Sofar Spotter json data downloaded through the Sofar API interface."""

    class Parameters(BaseModel, extra=Extra.forbid):

        read_csv_kwargs: Dict[str, Any] = {}
        from_dataframe_kwargs: Dict[str, Any] = {}

    parameters: Parameters = Parameters()

    def read(self, input_key: str) -> Union[xr.Dataset, Dict[str, xr.Dataset]]:
        # # Request requires that spotter belongs to the user (token)
        # url = "https://api.sofarocean.com/api/wave-data?"
        # payload = {
        #     "spotterId": "SPOT-1945",
        #     "startDate": "2021-09-01T00:00:00Z",
        #     "endDate": "2021-09-02T00:00:00Z",
        #     "includeWaves": "true",
        #     "includeSurfaceTempData": "true",
        #     "includeTrack": "false",  # Included in waves data
        #     "includeFrequencyData": "true",
        #     "includeDirectionalMoments": "true",
        #     "includePartitionData": "true",
        #     "includeBarometerData": "true",
        # }
        # headers = {"token": "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"}
        # res = requests.get(url, params=payload, headers=headers)

        # data = res.json()
        # with open('data.json', 'w') as f:
        #     json.dump(data, f)

        # Open retrieved data
        f = open(input_key)
        data = json.load(f)

        if "message" in data:
            raise PermissionError("Sofar API message: '" + data["message"] + "'")

        if ("waves" in data["data"]) and (not data["data"]["waves"]):
            raise EOFError("No data recorded.")

        # Fetch waves data
        waves = {}
        for nm in data["data"]["waves"][0]:
            waves[nm] = tuple(measurement[nm] for measurement in data["data"]["waves"])

        ds_waves = xr.Dataset()
        ds_waves["timestamp"] = xr.DataArray(
            np.array(waves.pop("timestamp"), dtype="datetime64[ns]"), dims=["timestamp"]
        )
        for nm in waves:
            ds_waves[nm] = xr.DataArray(np.array(waves[nm]), dims=["timestamp"])

        # Fetch sea temperature data
        ds_sst = xr.Dataset()
        if data["data"]["surfaceTemp"]:
            sst = {}
            for nm in data["data"]["surfaceTemp"][0]:
                sst[nm + "_sst"] = tuple(
                    measurement[nm] for measurement in data["data"]["surfaceTemp"]
                )

            ds_sst["timestamp"] = xr.DataArray(
                np.array(sst.pop("timestamp_sst"), dtype="datetime64[ns]"),
                dims=["timestamp"],
            )
            for nm in sst:
                ds_sst[nm] = xr.DataArray(np.array(sst[nm]), dims=["timestamp"])

        # Fetch barometric data
        ds_baro = xr.Dataset()
        if data["data"]["barometerData"]:
            baro = {}
            for nm in data["data"]["barometerData"][0]:
                baro[nm + "_baro"] = tuple(
                    measurement[nm] for measurement in data["data"]["barometerData"]
                )

            ds_baro["timestamp"] = xr.DataArray(
                np.array(baro.pop("timestamp_baro"), dtype="datetime64[ns]"),
                dims=["timestamp"],
            )
            for nm in baro:
                ds_baro[nm] = xr.DataArray(np.array(baro[nm]), dims=["timestamp"])

        # Fetch frequency data
        ds_freq = xr.Dataset()
        if data["data"]["frequencyData"]:
            freq = {}
            for nm in data["data"]["frequencyData"][0]:
                freq[nm] = tuple(
                    measurement[nm] for measurement in data["data"]["frequencyData"]
                )

            # Not going to bother reading these
            freq.pop("latitude")
            freq.pop("longitude")

            ds_freq["timestamp"] = xr.DataArray(
                np.array(freq.pop("timestamp"), dtype="datetime64[ns]"),
                dims=["timestamp"],
            )
            # Assume frequency vector doesn't change
            ds_freq["frequency"] = xr.DataArray(
                np.array(freq.pop("frequency")[0]), dims=["frequency"]
            )
            for nm in freq:
                ds_freq[nm] = xr.DataArray(
                    np.array(freq[nm]), dims=["timestamp", "frequency"]
                )
        else:  # Need to set frequency coordinate for tsdat
            ds_freq["frequency"] = xr.DataArray(np.array([0]), dims=["frequency"])

        ds_part = xr.Dataset()
        if data["data"]["partitionData"]:
            part = {}
            # Get partitions
            for nm in data["data"]["partitionData"][0]["partitions"][0]:
                part[nm + "Part0"] = tuple(
                    measurement["partitions"][0][nm]
                    for measurement in data["data"]["partitionData"]
                )
                part[nm + "Part1"] = tuple(
                    measurement["partitions"][1][nm]
                    for measurement in data["data"]["partitionData"]
                )
            # Get time/lat/lon
            for nm in data["data"]["partitionData"][0]:
                part[nm + "_part"] = tuple(
                    measurement[nm] for measurement in data["data"]["partitionData"]
                )
            part.pop("partitions_part")

            ds_part["timestamp"] = xr.DataArray(
                np.array(part.pop("timestamp_part"), dtype="datetime64[ns]"),
                dims=["timestamp"],
            )
            for nm in part:
                ds_part[nm] = xr.DataArray(np.array(part[nm]), dims=["timestamp"])

        ds = xr.merge((ds_waves, ds_sst, ds_baro, ds_freq, ds_part))
        ds.attrs["spotter_id"] = data["data"]["spotterId"]

        return ds
