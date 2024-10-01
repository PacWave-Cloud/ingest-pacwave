from typing import Dict, Union
import xarray as xr
from tsdat import DataReader
from mhkit import dolfyn


def calc_declination(time):
    # Estimate declination by current change of 0.01 deg W per year
    t = dolfyn.time.dt642date(time)[0]
    day_of_year = t.timetuple().tm_yday
    declin = 14.83 - (t.year - 2024 + day_of_year / 365.25) * 0.09

    return declin


class RDIReader(DataReader):
    """---------------------------------------------------------------------------------
    Reads a Teledyne RDI file from a FLOATr buoy deployed at PacWave. Checks that the
    instrument's orientation is set properly, and also adds the magnetic declination.
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
