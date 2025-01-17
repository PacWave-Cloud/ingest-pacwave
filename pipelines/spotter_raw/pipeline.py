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

    Ingests raw wave data pulled directly from Spotter buoys at PacWave, OR
    --------------------------------------------------------------------------------"""

    def hook_customize_dataset(self, dataset: xr.Dataset) -> xr.Dataset:
        # (Optional) Use this hook to modify the dataset before qc is applied
        dataset.attrs.pop("description")

        # Check buoy location
        dataset = set_pacwave_site(dataset)

        # Set spotter id attributes if loaded from json file
        spotter_id = Path(dataset.attrs["inputs"]).stem[4:].upper()
        dataset.attrs["qualifier"] = spotter_id
        datastream = dataset.attrs["datastream"].split(".")
        datastream[1] = dataset.attrs["dataset_name"] + "-" + dataset.attrs["qualifier"]
        dataset.attrs["datastream"] = ".".join(datastream)
        dataset.attrs["platform_id"] += spotter_id

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
        ax2.set(ylabel="Latitude [deg N]", xlabel="Longitude [deg E]")
        ax2.ticklabel_format(axis="both", style="plain", useOffset=False)
        ax2.set_axisbelow(True)
        ax2.grid()

        plot_file = self.get_ancillary_filepath(title="basic")
        fig.savefig(plot_file)

        plt.style.use("default")
        if ~dataset["sea_surface_temperature"].isnull().all():
            fig, ax = plt.subplots(3, 1, figsize=(10, 6), constrained_layout=True)
            ax[0].plot(
                dataset["time"],
                dataset["sea_surface_temperature"],
                ".-",
                label="Sea Surface Temperature",
                color=haline(0.15),
            )
            ax[0].plot(
                dataset["time"],
                dataset["air_temperature"],
                ".-",
                label="Air Temperature",
                color="black",
            )
            ax[0].set(ylabel="Temperature\n[deg C]")

            ax[1].plot(
                dataset["time"],
                dataset["air_pressure"],
                ".-",
                label="Air Pressure",
                color="black",
            )
            ax[1].set(ylabel="Pressure [hPa]")

            ax[2].plot(
                dataset["time"],
                dataset["humidity"],
                ".-",
                label="Relative Humidity",
                color="black",
            )
            ax[2].set(ylabel="Humidity [%]")

            for a in ax:
                a.legend(loc="upper left", bbox_to_anchor=[1.01, 1.0], handlelength=1.5)
            for a in ax[:-1]:
                a.set(xticklabels=[])
            ax[0].set(title=f"{dataset.datastream}")
            ax[-1].tick_params(labelrotation=45)
            ax[-1].xaxis.set_major_formatter(mdates.DateFormatter("%D %H"))
            ax[-1].set(xlabel="Time (UTC)")

            plot_file = self.get_ancillary_filepath(title="met")
            fig.savefig(plot_file)

        if ~dataset["solar_panel_voltage"].isnull().all():
            fig, ax = plt.subplots(3, 1, figsize=(10, 6), constrained_layout=True)
            ax[0].plot(
                dataset["time"],
                dataset["solar_panel_voltage"],
                ".-",
                label="Solar Panel Voltage",
                color=dense(0.15),
            )
            ax[0].plot(
                dataset["time"],
                dataset["battery_voltage"],
                ".-",
                label="Battery Voltage",
                color="black",
            )
            ax[0].set(ylabel="Voltage [V]")

            ax[1].plot(
                dataset["time"],
                dataset["solar_panel_current"],
                ".-",
                label="Solar Panel Current",
                color=dense(0.15),
            )
            ax[1].plot(
                dataset["time"],
                dataset["battery_current"],
                ".-",
                label="Battery Current",
                color="black",
            )
            ax[1].set(ylabel="Current [A]")

            ax[2].plot(
                dataset["time"],
                dataset["charge_state"],
                ".-",
                label="Charge State",
                color=dense(0.25),
            )
            ax[2].plot(
                dataset["time"],
                dataset["charge_fault"],
                ".-",
                label="Charge Fault",
                color=dense(0.9),
            )
            ax[2].set(ylabel="Flag")

            for a in ax:
                a.legend(loc="upper left", bbox_to_anchor=[1.01, 1.0], handlelength=1.5)
            for a in ax[:-1]:
                a.set(xticklabels=[])
            ax[0].set(title=f"{dataset.datastream}")
            ax[-1].tick_params(labelrotation=45)
            ax[-1].xaxis.set_major_formatter(mdates.DateFormatter("%D %H"))
            ax[-1].set(xlabel="Time (UTC)")

            plot_file = self.get_ancillary_filepath(title="battery")
            fig.savefig(plot_file)

    plt.close("all")
