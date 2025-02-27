import xarray as xr
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from cmocean.cm import amp_r, dense, haline
from tsdat import IngestPipeline

from shared.misc import set_pacwave_site


class SpotterAPI(IngestPipeline):
    """---------------------------------------------------------------------------------
    Pipeline for Spotter wave measurements pulled from the Sofar API.
    ---------------------------------------------------------------------------------"""

    def hook_customize_dataset(self, dataset: xr.Dataset) -> xr.Dataset:
        # (Optional) Use this hook to modify the dataset before qc is applied
        dataset.attrs.pop("description")

        # Remove empty frequency coordinate if needed:
        if not dataset["frequency"].all():
            dataset = dataset.drop_dims("frequency")

        # Drop any other empty vars. Empty frequency vars would have been dropped above
        to_drop = []
        for var in dataset.data_vars:
            if "frequency" not in dataset[var].coords:
                if dataset[var].isnull().all() or all(
                    dataset[var] == dataset[var]._FillValue
                ):
                    to_drop.append(var)
        dataset = dataset.drop_vars(to_drop)

        # Check if buoys are moved
        dataset = set_pacwave_site(dataset)

        # Convert CCW to East into CW from N
        for var in dataset.data_vars:
            if "dir" in var:
                dataset[var].values = (270 - dataset[var]) % 360

        # Set spotter id attributes if loaded from json file
        if hasattr(dataset, "spotter_id"):
            dataset.attrs["qualifier"] = dataset.attrs["spotter_id"].split("-")[-1]
            datastream = dataset.attrs["datastream"].split(".")
            datastream[1] = (
                dataset.attrs["dataset_name"] + "-" + dataset.attrs["qualifier"]
            )
            dataset.attrs["datastream"] = ".".join(datastream)
            dataset.attrs["platform_id"] = dataset.attrs.pop("spotter_id")

        return dataset

    def hook_finalize_dataset(self, dataset: xr.Dataset) -> xr.Dataset:
        # (Optional) Use this hook to modify the dataset after qc is applied
        # but before it gets saved to the storage area

        return dataset

    def hook_plot_dataset(self, dataset: xr.Dataset):
        # (Optional, recommended) Create plots.
        plt.style.use("default")  # clear any styles that were set before

        if "air_pressure" in dataset:
            n = 5
        else:
            n = 4
        if "sea_surface_temperature" not in dataset:
            n = 3

        fig, ax = plt.subplots(n, 1, figsize=(11, 7), constrained_layout=True)

        c1 = amp_r(0.10)
        ax[0].plot(
            dataset["time"].values,
            dataset["significant_wave_height"],
            ".-",
            label="Significant Wave Height",
            color=c1,
        )
        ax[0].set(ylabel="Height [m]")

        c1, c2 = dense(0.15), dense(0.50)
        ax[1].plot(
            dataset["time"].values,
            dataset["mean_wave_period"],
            ".-",
            label="Mean Period",
            color=c1,
        )
        ax[1].plot(
            dataset["time"].values,
            dataset["peak_wave_period"],
            ".-",
            label="Peak Period",
            color=c2,
        )
        ax[1].set(ylabel="Period [s]")

        c1, c2, c3, c4 = haline(0.10), haline(0.30), haline(0.50), haline(0.70)
        ax[2].plot(
            dataset["time"].values,
            dataset["peak_wave_direction"],
            ".-",
            label="Peak Direction",
            color=c1,
        )
        ax[2].plot(
            dataset["time"].values,
            dataset["mean_wave_direction"],
            ".-",
            label="Mean Direction",
            color=c2,
        )
        ax[2].plot(
            dataset["time"].values,
            dataset["peak_wave_spread"],
            ".-",
            label="Peak Spread",
            color=c3,
        )
        ax[2].plot(
            dataset["time"].values,
            dataset["mean_wave_spread"],
            ".-",
            label="Mean Spread",
            color=c4,
        )
        ax[2].set(ylabel="Direction [deg]")

        if "sea_surface_temperature" in dataset:
            ax[3].plot(
                dataset["time"].values,
                dataset["sea_surface_temperature"],
                ".-",
                label="Sea Surface Temperature",
                color="black",
            )
            ax[3].set(ylabel="Temperature\n[deg C]")

        if "air_pressure" in dataset:
            ax[4].plot(
                dataset["time"].values,
                dataset["air_pressure"],
                ".-",
                label="Air Pressure",
                color="black",
            )
            ax[4].set(ylabel="Pressure [hPa]")

        for a in ax:
            a.legend(loc="upper left", bbox_to_anchor=[1.01, 1.0], handlelength=1.5)
        for a in ax[:-1]:
            a.set(xticklabels=[])

        ax[0].set(title=f"{dataset.datastream}")
        ax[-1].tick_params(labelrotation=45)
        ax[-1].xaxis.set_major_formatter(mdates.DateFormatter("%D %H"))
        ax[-1].set(xlabel="Time (UTC)")

        plot_file = self.get_ancillary_filepath(title="wave_data_plots")
        fig.savefig(plot_file)  # type: ignore
