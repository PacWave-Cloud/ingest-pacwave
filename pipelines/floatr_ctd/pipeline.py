import xarray as xr
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from tsdat import IngestPipeline


class FLOATrCTD(IngestPipeline):
    """---------------------------------------------------------------------------------
    Pipeline for reading Seabird CTD data sent from the FLOATr buoy to the OSU server.
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
        # Set the format of the x-axis tick labels
        time_format = mdates.DateFormatter("%D %H")
        plt.style.use("default")  # clear any styles that were set before
        plt.style.use("shared/styling.mplstyle")

        # Physical
        fig, ax = plt.subplots(3, 1, figsize=(9, 8), constrained_layout=True)
        ax[0].plot(dataset["time"], dataset["water_temperature"])
        ax[0].set(ylabel="Temperature\n[degree C]", xticklabels=[])
        # ax[1].plot(dataset["time"], dataset["dissolved_oxygen"])
        # ax[1].set(ylabel="Dissolved Oxygen\n[mg/L]", xticklabels=[])
        ax[1].plot(dataset["time"], dataset["conductivity"])
        ax[1].set(ylabel="Conductivity\n[S/m]", xticklabels=[])
        ax[2].plot(dataset["time"], dataset["salinity"])
        ax[2].set(ylabel="Salinity [psu]", xticklabels=[])

        ax[0].set(title=f"{dataset.datastream}")
        ax[-1].tick_params(labelrotation=45)
        ax[-1].xaxis.set_major_formatter(time_format)
        ax[-1].set(xlabel="Time [UTC]")

        plot_file = self.get_ancillary_filepath(title="ctd")
        fig.savefig(plot_file)
        plt.close(fig)
