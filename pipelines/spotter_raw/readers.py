import xarray as xr
from tsdat import DataReader


class NetCDFReader(DataReader):
    """---------------------------------------------------------------------------------
    Thin wrapper around xarray's `open_dataset()` function, with optional parameters
    used as keyword arguments in the function call.

    ---------------------------------------------------------------------------------"""

    def read(self, input_key: str) -> xr.Dataset:
        dataset = xr.open_dataset(input_key)  # type: ignore

        if "sst_time" not in dataset.coords:
            dataset["sst_time"] = xr.DataArray(
                dataset["loc_time"].values, dims=["sst_time"]
            )
        if "htu_time" not in dataset.coords:
            dataset["htu_time"] = xr.DataArray(
                dataset["loc_time"].values, dims=["htu_time"]
            )
        if "baro_time" not in dataset.coords:
            dataset["baro_time"] = xr.DataArray(
                dataset["loc_time"].values, dims=["baro_time"]
            )
        return dataset
