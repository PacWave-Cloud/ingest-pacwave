from pathlib import Path
import pandas as pd
import xarray as xr
import matplotlib.pyplot as plt
from tsdat import IngestPipeline

from shared.misc import set_floatr_buoy_number
from utils import add_colorbar


class FLOATrADCP(IngestPipeline):
    """---------------------------------------------------------------------------------
    Pipeline for reading ADCP data sent from the FLOATr buoy to the OSU server.
    ---------------------------------------------------------------------------------"""

    def hook_customize_dataset(self, dataset: xr.Dataset) -> xr.Dataset:
        # (Optional) Use this hook to modify the dataset before qc is applied
        dataset.attrs.pop("description")
        dataset = set_floatr_buoy_number(dataset)

        return dataset

    def hook_finalize_dataset(self, dataset: xr.Dataset) -> xr.Dataset:
        # (Optional) Use this hook to modify the dataset after qc is applied
        # but before it gets saved to the storage area
        return dataset

    def hook_plot_dataset(self, dataset: xr.Dataset):
        # (Optional, recommended) Create plots.

        fig, ax = plt.subplots(
            nrows=2, ncols=1, figsize=(10, 5), constrained_layout=True
        )
        date = pd.to_datetime(dataset["time"].values)
        vele = ax[0].pcolormesh(
            date,
            -dataset["range"],
            dataset["vel_east"].T,
            cmap="coolwarm",
            shading="nearest",
            vmin=-0.5,
            vmax=0.5,
        )
        ax[0].set(title=f"{dataset.datastream}")
        ax[0].set_ylabel("Depth [m]")
        add_colorbar(ax[0], vele, "Velocity East [m/s]")

        veln = ax[1].pcolormesh(
            date,
            -dataset["range"],
            dataset["vel_north"].T,
            cmap="coolwarm",
            shading="nearest",
            vmin=-0.5,
            vmax=0.5,
        )
        ax[1].set_xlabel("Time (UTC)")
        ax[1].set_ylabel("Depth [m]")
        add_colorbar(ax[1], veln, "Velocity North [m/s]")

        plot_filepath = self.get_ancillary_filepath(title="adcp")
        fig.savefig(plot_filepath)
        plt.close(fig)
