import xarray as xr
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

from tsdat import IngestPipeline


class Waves(IngestPipeline):
    """--------------------------------------------------------------------------------
    SPOTTER BUOY INGESTION PIPELINE

    Ingests wave data recorded by a Spotter buoy at PacWave, OR
    --------------------------------------------------------------------------------"""

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
        # # Set the format of the x-axis tick labels
        # time_format = mdates.DateFormatter("%D %H")
        # plt.style.use("default")  # clear any styles that were set before
        # plt.style.use("shared/styling.mplstyle")

        # if "pos" in dataset.qualifier:
        #     fig, ax = plt.subplots()

        #     ax.plot(dataset.time, dataset["x"], label="surge")
        #     ax.plot(dataset.time, dataset["y"], label="sway")
        #     ax.plot(dataset.time, dataset["z"], label="heave")

        #     ax.set_title("")  # Remove bogus title created by xarray
        #     ax.legend(ncol=2, bbox_to_anchor=(1, -0.05))
        #     ax.set_ylabel("Buoy Displacement [m]")
        #     ax.set_xlabel("Time [UTC]")
        #     ax.xaxis.set_major_formatter(time_format)

        #     plot_file = self.get_ancillary_filepath(title="displacement")
        #     fig.savefig(plot_file)
        #     plt.close(fig)

        # elif "gps" in dataset.qualifier:
        #     fig, ax = plt.subplots()

        #     ax.scatter(dataset["lon"], dataset["lat"])
        #     ax.set(ylabel="Latitude [deg N]", xlabel="Longitude [deg E]")
        #     ax.ticklabel_format(axis="both", style="plain", useOffset=False)

        #     plot_file = self.get_ancillary_filepath(title="location")
        #     fig.savefig(plot_file)
        #     plt.close(fig)

        # elif "sst" in dataset.qualifier:
        #     fig, ax = plt.subplots()

        #     ax.plot(dataset["time"], dataset["sst"])
        #     ax.set(ylabel="SST [degC]", xlabel="Time [UTC]")
        #     ax.xaxis.set_major_formatter(time_format)

        #     plot_file = self.get_ancillary_filepath(title="location")
        #     fig.savefig(plot_file)
        #     plt.close(fig)
