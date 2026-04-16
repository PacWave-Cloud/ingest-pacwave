import numpy as np
import xarray as xr
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from cmocean.cm import dense, haline
from tsdat import IngestPipeline

from shared.misc import set_pacwave_site
from shared.writers import write_csv


class SpotterRaw(IngestPipeline):
    """--------------------------------------------------------------------------------
    SPOTTER BUOY INGESTION PIPELINE

    Ingests raw wave data pulled directly from Spotter buoys
    --------------------------------------------------------------------------------"""

    def hook_customize_dataset(self, dataset: xr.Dataset) -> xr.Dataset:
        # (Optional) Use this hook to modify the dataset before qc is applied
        dataset.attrs.pop("description")

        # Drop variables that aren't present in input dataset
        if "SST" not in dataset.attrs["sensors"]:
            dataset = dataset.drop_vars(
                "sea_surface_temperature", errors="ignore"
            ).drop_vars("time_sst", errors="ignore")
        if "HTU" not in dataset.attrs["sensors"]:
            dataset = (
                dataset.drop_vars("air_temperature", errors="ignore")
                .drop_vars("humidity", errors="ignore")
                .drop_vars("time_met", errors="ignore")
            )
        if "BARO" not in dataset.attrs["sensors"]:
            dataset = dataset.drop_vars("air_pressure", errors="ignore").drop_vars(
                "time_baro", errors="ignore"
            )

        # Set Lat/lon
        dataset["latitude"].values = np.array(
            dataset["latitude"] + dataset["lat_min"] * 1e-5 / 60
        )
        dataset["longitude"].values = np.array(
            dataset["longitude"] + dataset["lon_min"] * 1e-5 / 60
        )

        # Set spotter id attributes if loaded from json file
        if hasattr(dataset, "spotter_id"):
            dataset.attrs["qualifier"] = dataset.attrs["spotter_id"].split("-")[-1]
            datastream = dataset.attrs["datastream"].split(".")
            datastream[1] = (
                dataset.attrs["dataset_name"] + "-" + dataset.attrs["qualifier"]
            )
            dataset.attrs["datastream"] = ".".join(datastream)
            dataset.attrs["platform_id"] = dataset.attrs.pop("spotter_id")

        # Check buoy location
        dataset = set_pacwave_site(dataset)

        return dataset

    def hook_finalize_dataset(self, dataset: xr.Dataset) -> xr.Dataset:
        # (Optional) Use this hook to modify the dataset after qc is applied
        # but before it gets saved to the storage area

        # Save csv file
        ds = dataset.copy(deep=True)
        for t in ds.coords:
            if "_" in t:
                ds = ds.interp({t: dataset["time"]}, method="nearest")
                ds = ds.drop_vars(t)
        write_csv(ds)

        return dataset

    def hook_plot_dataset(self, dataset: xr.Dataset):
        # (Optional, recommended) Create plots.

        # Set the format of the x-axis tick labels
        time_format = mdates.DateFormatter("%D")
        plt.style.use("default")  # clear any styles that were set before
        plt.style.use("shared/styling.mplstyle")

        if "sea_surface_temperature" not in dataset.data_vars:
            fig = plt.figure(figsize=(12, 4), constrained_layout=True)
            gs = fig.add_gridspec(1, 3)
            ax1 = fig.add_subplot(gs[:, :-1])
            ax2 = fig.add_subplot(gs[:, -1])
        else:
            fig = plt.figure(figsize=(12, 8), constrained_layout=True)
            gs = fig.add_gridspec(6, 3)
            ax1 = fig.add_subplot(gs[:3, :-1])
            ax2 = fig.add_subplot(gs[:3, -1])
            ax3 = fig.add_subplot(gs[3, :-1])
            ax4 = fig.add_subplot(gs[4, :-1])
            ax5 = fig.add_subplot(gs[5, :-1])

        ax1.plot(dataset["time"], dataset["x"], label="Surge")
        ax1.plot(dataset["time"], dataset["y"], label="Sway")
        ax1.plot(dataset["time"], dataset["z"], label="Heave")
        ax1.set(title=f"{dataset.datastream}")
        ax1.legend(ncol=3, loc="upper center")
        ax1.set_ylabel("Buoy\nDisplacement [m]")

        ax2.scatter(dataset["longitude"], dataset["latitude"])
        ax2.set(
            ylabel="Latitude [deg N]",
            xlabel="Longitude [deg E]",
            xlim=(dataset["longitude"].warn_min, dataset["longitude"].warn_max),
            ylim=(dataset["latitude"].warn_min, dataset["latitude"].warn_max),
        )
        # ax2.ticklabel_format(axis="both", style="plain", useOffset=False)
        ax2.set_axisbelow(True)
        ax2.grid()

        if "sea_surface_temperature" not in dataset.data_vars:
            ax1.tick_params(labelrotation=45)
            ax1.xaxis.set_major_formatter(time_format)
            ax1.set(xlabel="Time (UTC)")

        if "sea_surface_temperature" in dataset.data_vars:
            ax3.plot(
                dataset["time_sst"],
                dataset["sea_surface_temperature"],
                ".-",
                label="Sea Surface",
                color=haline(0.15),
            )
            ax3.plot(
                dataset["time_met"],
                dataset["air_temperature"],
                ".-",
                label="Air",
                color="black",
            )
            ax3.set(ylabel="Temperature\n[deg C]")

            ax4.plot(
                dataset["time_baro"],
                dataset["air_pressure"],
                ".-",
                color="black",
            )
            ax4.set(ylabel="Air Pressure\n[hPa]")

            ax5.plot(
                dataset["time_met"],
                dataset["humidity"],
                ".-",
                color="black",
            )
            ax5.set(ylabel="Relative\nHumidity [%]")

            ax3.legend(
                ncol=2,
                loc="upper center",
                handlelength=1.5,
            )
            for a in [ax1, ax3, ax4]:
                a.set(xticklabels=[])
            ax5.tick_params(labelrotation=45)
            ax5.xaxis.set_major_formatter(time_format)
            ax5.set(xlabel="Time (UTC)")

        plot_file = self.get_ancillary_filepath(title="raw")
        fig.savefig(plot_file)

    plt.close("all")
