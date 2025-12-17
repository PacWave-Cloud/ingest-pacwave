from typing import Dict, Union
from pydantic import BaseModel, Extra
import xarray as xr
import mhkit.dolfyn as dolfyn
from mhkit.dolfyn.adp import api
from tsdat import DataReader


class Sig250Reader(DataReader):
    class Parameters(BaseModel, extra=Extra.forbid):
        depth_offset: float = 0.5
        salinity: float = 35
        correlation_filter_threshold: float = 30
        ast_quality_threshold: float = 30
        le_quality_threshold: float = 30

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

    def processing_altimeter(self, ds):
        ds["ast_dist_alt"] = ds["ast_dist_alt"].where(
            ds["ast_quality_alt"] > self.parameters.ast_quality_threshold
        )
        ds["le_dist_alt"] = ds["le_dist_alt"].where(
            ds["le_quality_alt"] > self.parameters.le_quality_threshold
        )
        return ds

    def read(self, input_key: str) -> Union[xr.Dataset, Dict[str, xr.Dataset]]:
        """-------------------------------------------------------------------
        Reads the waves profile from the PacWave Sig250. Velocity data is
        averged in the sig250_avgd pipeline.

        Args:
            filename (str): The path to the ADCP file to read in.

        Returns:
            xr.Dataset: An xr.Dataset object
        -------------------------------------------------------------------"""

        # Read raw binary files
        ds_waves, ds_avg = dolfyn.read(input_key)

        # Conduct basic processing
        ds_waves = self.processing(ds_waves)
        ds_waves = self.processing_altimeter(ds_waves)

        return ds_waves
