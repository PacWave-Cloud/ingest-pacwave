import numpy as np
import xarray as xr
from typing import Dict
import matplotlib.pyplot as plt
from mhkit import wave, dolfyn
from cmocean.cm import amp_r, dense, haline

from tsdat import TransformationPipeline


fs = 2.5  # Hz, Spotter sampling frequency
wat = 1800  # s, window averaging time
freq_slc = [0.0455, 1]  # 22 to 1 s periods


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
        return dataset

    def hook_finalize_dataset(self, dataset: xr.Dataset) -> xr.Dataset:
        # (Optional) Use this hook to modify the dataset after qc is applied
        # but before it gets saved to the storage area
        return dataset

    def hook_plot_dataset(self, dataset: xr.Dataset):
        # (Optional, recommended) Create plots.
        pass
