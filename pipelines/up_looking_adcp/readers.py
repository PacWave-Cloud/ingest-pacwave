from typing import Dict, Union
from pydantic import BaseModel, Extra
import pandas as pd
import xarray as xr

from tsdat import DataReader
import mhkit.dolfyn as dolfyn
from mhkit.dolfyn.adp import api


def calc_declination(time):
    # Estimate declination by current change of 0.01 deg W per year
    t = pd.Timestamp(time[0].values)
    day_of_year = t.timetuple().tm_yday
    declin = 14.83 - (t.year - 2024 + day_of_year / 365.25) * 0.09

    return declin


class UpFacingADCPReader(DataReader):
    """---------------------------------------------------------------------------------
    Custom DataReader that can be used to read data from a specific format.

    Built-in implementations of data readers can be found in the
    [tsdat.io.readers](https://tsdat.readthedocs.io/en/latest/autoapi/tsdat/io/readers)
    module.

    ---------------------------------------------------------------------------------"""

    class Parameters(BaseModel, extra=Extra.forbid):
        """If your CustomDataReader should take any additional arguments from the
        retriever configuration file, then those should be specified here.

        e.g.,:
        custom_parameter: float = 5.0

        """

        depth_offset: float = 0.5
        salinity: float = 35

    parameters: Parameters = Parameters()
    """Extra parameters that can be set via the retrieval configuration file. If you opt
    to not use any configuration parameters then please remove the code above."""

    def read(self, input_key: str) -> Union[xr.Dataset, Dict[str, xr.Dataset]]:
        """-------------------------------------------------------------------
        SigVM datafiles are a zip folder containing two files, a .anpp file
        and a .ad2cp file. This reader skips the first .anpp file and reads
        the raw data from the .ad2cp file.

        Args:
            filename (str): The path to the ADCP file to read in.

        Returns:
            xr.Dataset: An xr.Dataset object
        -------------------------------------------------------------------"""

        ds_waves, ds_avg = dolfyn.read(input_key)

        for ds in [ds_waves, ds_avg]:
            # Set depth below water surface
            api.clean.set_range_offset(ds, self.parameters.depth_offset)
            api.clean.water_depth_from_pressure(ds, salinity=self.parameters.salinity)

            # Rotate to Earth coordinates
            try:
                declin = calc_declination(ds["time"])
            except Exception:
                declin = calc_declination(ds["time_avg"])
            dolfyn.set_declination(ds, declin)
            dolfyn.rotate2(ds, "earth")

        ds = xr.merge([ds_waves, ds_avg], compat="override")
        ds.attrs.update(ds_avg.attrs)

        return ds
