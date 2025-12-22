from pathlib import Path
import xarray as xr
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from cmocean.cm import dense, haline
from tsdat import IngestPipeline

from shared.misc import set_pacwave_site


class SpotterRaw(IngestPipeline):
    """--------------------------------------------------------------------------------
    SPOTTER BUOY INGESTION PIPELINE

    Ingests raw wave data pulled directly from Spotter buoys
    --------------------------------------------------------------------------------"""

    def hook_customize_dataset(self, dataset: xr.Dataset) -> xr.Dataset:
        # (Optional) Use this hook to modify the dataset before qc is applied
        dataset.attrs.pop("description")

        # Check if buoys are moved
        dataset = set_pacwave_site(dataset)

        # Fix messed up time coordinate. Occurs when datasets are merged.
        for coord in dataset.coords:
            if "time" in coord:
                dataset = dataset.assign_coords(
                    {coord: dataset[coord].astype("datetime64[ns]")}
                )
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

        fig = plt.figure(figsize=(14, 6), constrained_layout=True)
        gs = fig.add_gridspec(1, 3)
        ax1 = fig.add_subplot(gs[:-1])
        ax2 = fig.add_subplot(gs[-1])

        ax1.plot(dataset["time"], dataset["x"], label="surge")
        ax1.plot(dataset["time"], dataset["y"], label="sway")
        ax1.plot(dataset["time"], dataset["z"], label="heave")
        ax1.tick_params(labelrotation=45)

        ax1.set(title=f"{dataset.datastream}")
        ax1.legend(ncol=3, loc="upper left", bbox_to_anchor=(0.25, 1.01))
        ax1.set_ylabel("Buoy Displacement [m]")
        ax1.set_xlabel("Time [UTC]")
        ax1.xaxis.set_major_formatter(time_format)

        ax2.scatter(dataset["longitude"], dataset["latitude"])
        ax2.set(
            ylabel="Latitude [deg N]",
            xlabel="Longitude [deg E]",
            xlim=(dataset["longitude"].warn_min, dataset["longitude"].warn_max),
            ylim=(dataset["latitude"].warn_min, dataset["latitude"].warn_max),
        )
        ax2.ticklabel_format(axis="both", style="plain", useOffset=False)
        ax2.set_axisbelow(True)
        ax2.grid()

        plot_file = self.get_ancillary_filepath(title="basic")
        fig.savefig(plot_file)
        plt.close()
