from typing import Dict, Union
import numpy as np
import pandas as pd
import xarray as xr
from datetime import datetime, time as dtime
from mhkit import dolfyn

from tsdat import DataReader


def calc_declination(time):
    # Estimate declination by current change of 0.01 deg W per year
    t = dolfyn.time.dt642date(time)[0]
    day_of_year = t.timetuple().tm_yday
    declin = 14.83 - (t.year - 2024 + day_of_year / 365.25) * 0.09

    return declin


class RDIReader(DataReader):
    """---------------------------------------------------------------------------------
    Custom DataReader that can be used to read data from a specific format.

    Built-in implementations of data readers can be found in the
    [tsdat.io.readers](https://tsdat.readthedocs.io/en/latest/autoapi/tsdat/io/readers)
    module.

    ---------------------------------------------------------------------------------"""

    def read(self, input_key: str) -> Union[xr.Dataset, Dict[str, xr.Dataset]]:
        ds = dolfyn.read(input_key)

        # Check that orientation is set properly given a "down-looking" orientation
        if "down" not in ds.orientation:
            ds.velds.rotate2("inst")
            ds.attrs["orientation"] = "down"
            ds = ds.drop_vars("orientmat")
            ds["orientmat"] = dolfyn.rotate.rdi._calc_orientmat(ds)
            ds.velds.rotate2("earth")

        # reset Bin 1 distance as distance from ADCP transducers
        ds.attrs["bin1_dist_m"] = ds.blank_dist + ds.cell_size
        reset_range = ds.bin1_dist_m + np.arange(ds["range"].size) * ds.cell_size
        ds = ds.assign_coords({"range": reset_range})

        declin = calc_declination(ds.time)
        ds.velds.set_declination(round(declin, 2))

        # Set speed and direction
        ds["U_mag"] = ds.velds.U_mag
        ds["U_dir"] = ds.velds.U_dir

        # Convert from [0, 360] back to [-180, 180]
        u_dir = ds["U_dir"].values
        u_dir[u_dir > 180] -= 360
        ds["U_dir"].values = u_dir

        # Transpose [dir, range, time] to [time, range, dir]
        ds = ds.transpose()

        return ds
