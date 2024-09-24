import xarray as xr
from typing import Dict
from tsdat import TransformationPipeline

from shared.misc import set_pacwave_site


class VapSpotterRaw(TransformationPipeline):
    """--------------------------------------------------------------------------------
    SPOTTER BUOY VAP PIPELINE

    Combines wave data recorded by a Spotter buoy at PacWave, OR
    --------------------------------------------------------------------------------"""

    def hook_customize_input_datasets(self, input_datasets) -> Dict[str, xr.Dataset]:
        # Code hook to customize any input datasets prior to datastreams being combined
        # and data converters being run.
        return input_datasets

    def hook_customize_dataset(self, dataset: xr.Dataset) -> xr.Dataset:
        # (Optional) Use this hook to modify the dataset before qc is applied
        # Check if buoys are moved
        dataset = set_pacwave_site(dataset)

        return dataset

    def hook_finalize_dataset(self, dataset: xr.Dataset) -> xr.Dataset:
        # (Optional) Use this hook to modify the dataset after qc is applied
        # but before it gets saved to the storage area
        return dataset

    def hook_plot_dataset(self, dataset: xr.Dataset):
        # (Optional, recommended) Create plots.
        pass
