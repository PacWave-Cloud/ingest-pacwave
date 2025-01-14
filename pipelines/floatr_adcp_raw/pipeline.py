import pandas as pd
import xarray as xr
import matplotlib.pyplot as plt
from tsdat import IngestPipeline

from utils import add_colorbar


class FLOATrADCPRaw(IngestPipeline):
    """---------------------------------------------------------------------------------
    Pipeline for reading raw ADCP data pulled directly from the ADCP on the FLOATr buoy.
    ---------------------------------------------------------------------------------"""
    def hook_customize_dataset(self, dataset: xr.Dataset) -> xr.Dataset:
        # (Optional) Use this hook to modify the dataset before qc is applied
        dataset.attrs.pop("description")

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
            dataset["range"],
            dataset["vel"][:, :, 0].T,
            cmap="Blues",
            shading="nearest",
        )
        ax[0].set_ylabel(r"Range [m]")
        add_colorbar(ax[0], vele, "Velocity E [m/s]")

        veln = ax[1].pcolormesh(
            date,
            dataset["range"],
            dataset["vel"][:, :, 1].T,
            cmap="Blues",
            shading="nearest",
        )
        ax[1].set_xlabel("Time (UTC)")
        ax[1].set_ylabel(r"Range [m]")
        add_colorbar(ax[1], veln, "Velocity N [m/s]")

        plot_filepath = self.get_ancillary_filepath(title="adcp")
        fig.savefig(plot_filepath)
        plt.close(fig)
