from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Extra, Field
from pathlib import Path
import csv
import xarray as xr

from tsdat import FileWriter
from tsdat.config.storage import StorageConfig
from tsdat.config.utils import recursive_instantiate


def create_storage_class():
    """----------------------------------------------------------------------------
    Creates generic Tsdat storage class
    ----------------------------------------------------------------------------"""
    parameters = {
        "storage_root": ".",
        "data_storage_path": Path(
            "{location_id}/{dataset_name}/{qualifier}/data/{year}/{month}/{day}"
        ),
    }
    storage_model = StorageConfig(
        classname="tsdat.io.storage.FileSystem", parameters=parameters
    )
    return storage_model


def create_storage_class_S3():
    """----------------------------------------------------------------------------
    Creates generic Tsdat storage class
    ----------------------------------------------------------------------------"""
    parameters = {
        "storage_root": ".",
        "data_storage_path": Path(
            "{location_id}/{dataset_name}/{qualifier}/data/{year}/{month}/{day}"
        ),
    }
    storage_model = StorageConfig(
        classname="tsdat.io.storage.FileSystemS3", parameters=parameters
    )
    return storage_model


def write_csv(dataset):
    """----------------------------------------------------------------------------
    Saves pipeline data in a parquet format using a custom writer

    Args:
        dataset (xarray.dataset): Pipeline dataset
        instrument (str): Instrument handle, for use in data filepath

    ----------------------------------------------------------------------------"""
    try:
        storage_model = create_storage_class_S3()
        storage = recursive_instantiate(storage_model)
    except:
        storage_model = create_storage_class()
        storage = recursive_instantiate(storage_model)
    storage.handler.writer = CSVWriter()
    storage.save_data(dataset)


class CSVWriter(FileWriter):
    """---------------------------------------------------------------------------------
    Converts a `xr.Dataset` object to a pandas `DataFrame` and saves the result to a csv
    file using `pd.DataFrame.to_csv()`. Properties under the `to_csv_kwargs` parameter
    are passed to `pd.DataFrame.to_csv()` as keyword arguments.
    ---------------------------------------------------------------------------------"""

    class Parameters(BaseModel, extra=Extra.forbid):
        dim_order: Optional[List[str]] = None
        to_csv_kwargs: Dict[str, Any] = Field(
            default_factory=lambda: dict(date_format="%Y-%m-%d %H:%M:%S.%f %Z")
        )

    parameters: Parameters = Parameters()
    file_extension: str = ".csv"

    def write(self, dataset: xr.Dataset, filepath: Optional[Path] = None) -> None:
        # Reset filepath
        filepath = filepath.with_suffix(self.file_extension)

        # Fetch dataset atttributes and create a list to write
        global_header = [[k, v] for k, v in dataset.attrs.items()]

        # Fetch variable attributes and collect them into rows
        var_headers = {
            "name": ["name"],
            "units": ["units"],
            "long_name": ["long_name"],
            "standard_name": ["standard_name"],
            "fill_value": ["fill_value"],
            "valid_min": ["valid_min"],
            "valid_max": ["valid_max"],
            "ancillary_variables": ["ancillary_variables"],
        }
        for var in dataset.data_vars:
            attrs = dataset[var]
            var_headers["name"].append(var)
            var_headers["units"].append(getattr(attrs, "units", ""))
            var_headers["long_name"].append(getattr(attrs, "long_name", ""))
            var_headers["standard_name"].append(getattr(attrs, "standard_name", ""))
            var_headers["fill_value"].append(getattr(attrs, "_FillValue", ""))
            var_headers["valid_min"].append(getattr(attrs, "valid_min", ""))
            var_headers["valid_max"].append(getattr(attrs, "valid_max", ""))
            var_headers["ancillary_variables"].append(
                getattr(attrs, "ancillary_variables", "")
            )

        # Open the file in write mode with newline='' to prevent extra blank rows
        with open(filepath, "w", newline="") as csvfile:
            writer = csv.writer(csvfile)
            # Write global attributes
            for h in global_header:
                writer.writerow(h)
            writer.writerow("\n")
            # Write variable attributes
            for vh in var_headers:
                writer.writerow(var_headers[vh])
            writer.writerow("\n")

        df = dataset.to_dataframe()
        df = df.tz_localize(dataset["time"].timezone, level=0)
        df.to_csv(filepath, mode="a", **self.parameters.to_csv_kwargs)  # type: ignore
