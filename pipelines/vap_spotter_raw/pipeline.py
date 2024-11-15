from typing import Dict
import xarray as xr
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from tsdat import TransformationPipeline

from shared.misc import set_pacwave_site


class VapSpotterRaw(TransformationPipeline):
    """--------------------------------------------------------------------------------
    SPOTTER BUOY VAP PIPELINE

    Combines wave measurements ingested from data pulled from Spotter buoys at 
    PacWave, OR
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
        # Set the format of the x-axis tick labels
        time_format = mdates.DateFormatter("%D %H")
        plt.style.use("default")  # clear any styles that were set before
        plt.style.use("shared/styling.mplstyle")

        # Plot buoy motion
        fig, ax = plt.subplots(figsize=(8,5))

        ax.plot(dataset.time, dataset["x"], label="surge")
        ax.plot(dataset.time, dataset["y"], label="sway")
        ax.plot(dataset.time, dataset["z"], label="heave")

        ax.set_title("")  # Remove bogus title created by xarray
        ax.legend(ncol=2, bbox_to_anchor=(1, -0.05))
        ax.set_ylabel("Buoy Displacement [m]")
        ax.set_xlabel("Time [UTC]")
        ax.set_xticklabels(ax.get_xticks(), rotation=45)
        ax.xaxis.set_major_formatter(time_format)

        plot_file = self.get_ancillary_filepath(title="displacement")
        fig.savefig(plot_file)
        plt.close(fig)

        # Plot GPS
        fig, ax = plt.subplots(figsize=(8,5))

        ax.scatter(dataset["longitude"], dataset["latitude"])
        ax.set(ylabel="Latitude [deg N]", xlabel="Longitude [deg E]")
        ax.ticklabel_format(axis="both", style="plain", useOffset=False)

        plot_file = self.get_ancillary_filepath(title="location")
        fig.savefig(plot_file)
        plt.close(fig)

        # Plot sea surface temperature
        fig, ax = plt.subplots(figsize=(8,5))

        ax.plot(dataset["time"], dataset["sst"])
        ax.set(ylabel="SST [degC]", xlabel="Time [UTC]")
        ax.set_xticklabels(ax.get_xticks(), rotation=45)
        ax.xaxis.set_major_formatter(time_format)
        
        plot_file = self.get_ancillary_filepath(title="sst")
        fig.savefig(plot_file)
        plt.close(fig)
