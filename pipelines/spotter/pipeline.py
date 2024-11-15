import act
import xarray as xr
import matplotlib.pyplot as plt
from cmocean.cm import amp_r, dense, haline
from tsdat import IngestPipeline

from shared.misc import set_pacwave_site


class SpotterAPI(IngestPipeline):
    """---------------------------------------------------------------------------------
    Pipeline for Spotter wave measurements pulled from the Sofar API.
    ---------------------------------------------------------------------------------"""

    def hook_customize_dataset(self, dataset: xr.Dataset) -> xr.Dataset:
        # (Optional) Use this hook to modify the dataset before qc is applied

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
            datastream[1] = dataset.attrs["dataset_name"] + "-" + dataset.attrs["qualifier"]
            dataset.attrs["datastream"] = ".".join(datastream)
            dataset.attrs["platform_id"] = dataset.attrs.pop("spotter_id")

        return dataset

    def hook_finalize_dataset(self, dataset: xr.Dataset) -> xr.Dataset:
        # (Optional) Use this hook to modify the dataset after qc is applied
        # but before it gets saved to the storage area

        return dataset

    def hook_plot_dataset(self, dataset: xr.Dataset):
        # (Optional, recommended) Create plots.
        display = act.plotting.TimeSeriesDisplay(
            dataset, subplot_shape=(3,), figsize=(15, 10)
        )

        c1 = amp_r(0.10)
        display.plot(
            "significant_wave_height",
            subplot_index=(0,),
            label="Significant Wave Height",
            color=c1,
        )
        plt.legend()

        c1, c2 = dense(0.15), dense(0.50)
        display.plot(
            "mean_wave_period", subplot_index=(1,), label="Mean Period", color=c1
        )
        display.plot(
            "peak_wave_period", subplot_index=(1,), label="Peak Period", color=c2
        )
        plt.legend()

        c1, c2, c3, c4 = haline(0.10), haline(0.30), haline(0.50), haline(0.70)
        display.plot(
            "peak_wave_direction", subplot_index=(2,), label="Peak Direction", color=c1
        )
        display.plot(
            "mean_wave_direction", subplot_index=(2,), label="Mean Direction", color=c2
        )
        display.plot(
            "peak_wave_spread",
            subplot_index=(2,),
            label="Peak Directional Spread",
            color=c3,
        )
        display.plot(
            "mean_wave_spread",
            subplot_index=(2,),
            label="Mean Directional Spread",
            color=c4,
        )
        plt.legend()

        plot_file = self.get_ancillary_filepath(title="wave_data_plots")
        plt.savefig(plot_file)  # type: ignore
