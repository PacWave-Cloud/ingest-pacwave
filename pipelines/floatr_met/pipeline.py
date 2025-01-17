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
        fig = plt.figure(figsize=(15, 8), constrained_layout=True)
        gs = fig.add_gridspec(5, 3)
        ax0 = fig.add_subplot(gs[2:, -1])
        ax1 = fig.add_subplot(gs[0, :-1])
        ax2 = fig.add_subplot(gs[1, :-1])
        ax3 = fig.add_subplot(gs[2, :-1])
        ax4 = fig.add_subplot(gs[3, :-1])
        ax5 = fig.add_subplot(gs[4, :-1])

        # Plot data
        ax1.plot(dataset["time"], dataset["air_pressure"])
        ax1.set(ylabel="Pressure\n[mbar]", xticklabels=[])
        ax2.plot(dataset["time"], dataset["air_temperature"])
        ax2.set(ylabel="Temperature\n[degree C]", xticklabels=[])
        ax3.plot(dataset["time"], dataset["windspeed"])
        ax3.set(ylabel="Wind Speed\n[m/s]", xticklabels=[])
        ax4.plot(dataset["time"], dataset["wind_dir_true"])
        ax4.set(ylabel="Wind Direction\n[degree]", xticklabels=[])
        ax5.plot(dataset["time"], dataset["shortwave_rad_1"], label="Sensor 1")
        ax5.plot(dataset["time"], dataset["shortwave_rad_2"], label="Sensor 2")
        ax5.set(ylabel="Shortwave\nRad [W/m$^2$]", xlabel="Time (UTC)")
        ax5.legend(loc="lower right", bbox_to_anchor=(1, 1), ncol=2, handlelength=1)

        ax1.set(title=f"{dataset.datastream}")
        ax5.tick_params(labelrotation=45)
        ax5.xaxis.set_major_formatter(time_format)

        # Plot GPS
        ax0.scatter(dataset["longitude"], dataset["latitude"])
        ax0.set(ylabel="Latitude [deg N]", xlabel="Longitude [deg E]")
        ax0.ticklabel_format(axis="both", style="plain", useOffset=False)
        ax0.set_axisbelow(True)
        ax0.grid()

        plot_file = self.get_ancillary_filepath(title="met")
        fig.savefig(plot_file)
        plt.close(fig)
