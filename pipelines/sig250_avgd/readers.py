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


class Sig250Reader(DataReader):
    class Parameters(BaseModel, extra=Extra.forbid):
        depth_offset: float = 0.5
        salinity: float = 35
        correlation_filter_threshold: float = 30

    parameters: Parameters = Parameters()

    def processing(self, ds, tag="") -> xr.Dataset:
        # The ADCP transducers were measured to be 0.5 m from the feet of the lander
        api.clean.set_range_offset(ds, self.parameters.depth_offset)
        # Calculate water depth
        api.clean.water_depth_from_pressure(ds, salinity=self.parameters.salinity)
        # Reduce depth measurement by 2 m
        ds["depth" + tag] = ds["depth" + tag] - 2
        # Remove surface sidelobe interference and low correlation values
        ds = api.clean.remove_surface_interference(ds)
        ds = api.clean.correlation_filter(
            ds, thresh=self.parameters.correlation_filter_threshold
        )
        # Correct magnetic declination
        declin = calc_declination(ds["time" + tag])
        dolfyn.set_declination(ds, declin, inplace=True)  # 14.8 deg Eastz
        dolfyn.rotate2(ds, "earth")

        return ds

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

        # Read raw binary files
        ds_avg = dolfyn.read(input_key)

        # Conduct basic processing
        ds_avg = self.processing(ds_avg, tag="_avg")

        # Calculate speed and direction from averaging profiles
        ds_avg["U_mag"] = ds_avg.velds.U_mag
        ds_avg["U_dir"] = ds_avg.velds.U_dir

        # Hack because coords can't get renamed
        ds_avg["time"] = ds_avg["time_avg"]

        return ds_avg
