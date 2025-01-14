import xarray as xr
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from tsdat import IngestPipeline


class FLOATrMET(IngestPipeline):
    """---------------------------------------------------------------------------------
    Pipeline for reading Campbell MET data sent from the FLOATr buoy to the OSU server.
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
        fig, ax = plt.subplots(5, 1, figsize=(10,7))
        ax[0].plot(dataset.time, dataset["air_pressure"])
        ax[0].set(ylabel="Pressure\n[mbar]")
        ax[1].plot(dataset.time, dataset["air_temperature"])
        ax[1].set(ylabel="Temperature\n[degree C]")
        ax[2].plot(dataset.time, dataset["windspeed"])
        ax[2].set(ylabel="Wind Speed\n[m/s]")
        ax[3].plot(dataset.time, dataset["wind_dir_true"])
        ax[3].set(ylabel="Wind Direction\n[degree]")
        ax[4].plot(dataset.time, dataset["shortwave_rad_1"])
        ax[4].plot(dataset.time, dataset["shortwave_rad_2"])
        ax[4].set(ylabel="Shortwave\nRad [W/m^2]")

        for a in ax:
            a.set(xticklabels=[])
        ax[4].set_xticklabels(ax[4].get_xticks(), rotation=45)
        ax[4].xaxis.set_major_formatter(time_format)

        plot_file = self.get_ancillary_filepath(title="met")
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