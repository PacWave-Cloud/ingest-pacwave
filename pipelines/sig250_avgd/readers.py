from typing import Dict, Union
from pydantic import BaseModel, Extra
import xarray as xr
from tsdat import DataReader
import mhkit.dolfyn as dolfyn
from mhkit.dolfyn.adp import api


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
        # Remove surface sidelobe interference and low correlation values
        ds = api.clean.remove_surface_interference(ds)
        ds = api.clean.correlation_filter(
            ds, thresh=self.parameters.correlation_filter_threshold
        )
        return ds

    def read(self, input_key: str) -> Union[xr.Dataset, Dict[str, xr.Dataset]]:
        """-------------------------------------------------------------------
        Reads averaged velocity data from Sig250 deployed at PacWave.

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

        # Add time variable because coords can't get renamed directly
        ds_avg["time"] = ds_avg["time_avg"]

        # Update rotate_vars attribute to reflect changes
        rotate_vars = []
        for ky in ds_avg.attrs["rotate_vars"]:
            rotate_vars.append(ky.replace("_avg", ""))
        ds_avg.attrs["rotate_vars"] = rotate_vars

        return ds_avg
