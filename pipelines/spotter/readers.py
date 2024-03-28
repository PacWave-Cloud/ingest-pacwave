from typing import Any, Dict, Union
from pydantic import BaseModel, Extra
import numpy as np
import pandas as pd
import xarray as xr
from tsdat import DataReader


class SpotterCSVReader(DataReader):
    """Custom DataReader that can be used to read data from a specific format.

    Built-in implementations of data readers can be found in the tsdat.io.readers
    module.
    """

    class Parameters(BaseModel, extra=Extra.forbid):
        """If your CustomDataReader should take any additional arguments from the
        retriever configuration file, then those should be specified here."""

        read_csv_kwargs: Dict[str, Any] = {}
        from_dataframe_kwargs: Dict[str, Any] = {}

    parameters: Parameters = Parameters()
    """Extra parameters that can be set via the retrieval configuration file. If you opt
    to not use any configuration parameters then please remove the code above."""

    def read(self, input_key: str) -> Union[xr.Dataset, Dict[str, xr.Dataset]]:
        # Read csv file with pandas
        df = pd.read_csv(input_key, **self.parameters.read_csv_kwargs)
        # Convert missing data (-) to nan
        df = df.replace("-", np.nan)
        # Set index
        df["Epoch Time"] = df["Epoch Time"].astype("int64") * 1e9
        df.index = df["Epoch Time"]

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
                coords={"Epoch Time": df_var.index, "index": range(df_var.shape[-1])},
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
