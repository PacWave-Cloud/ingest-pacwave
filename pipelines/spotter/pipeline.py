import act
import pytz
import xarray as xr
import matplotlib.pyplot as plt
from datetime import datetime
from cmocean.cm import amp_r, dense, haline
from tsdat import IngestPipeline, get_start_date_and_time_str, get_code_version

from shared.writers import write_csv


class Pacwave(IngestPipeline):
    """---------------------------------------------------------------------------------
    This is an example ingestion pipeline meant to demonstrate how one might set up a
    pipeline using this template repository.

    ---------------------------------------------------------------------------------"""

    def hook_customize_dataset(self, dataset: xr.Dataset) -> xr.Dataset:
        # (Optional) Use this hook to modify the dataset before qc is applied

        # Check if buoys are moved
        if dataset["latitude"].mean() > 44.6:
            dataset.attrs['location_id'] = "pwn"
        else:
            dataset.attrs['location_id'] = "pws"

        return dataset

    def hook_finalize_dataset(self, dataset: xr.Dataset) -> xr.Dataset:
        # (Optional) Use this hook to modify the dataset after qc is applied
        # but before it gets saved to the storage area

        # Drop 2D Variables from csv dataset
        to_drop = ["frequency", "wave_a1_value", "wave_b1_value", "wave_a2_value", "wave_b2_value", "wave_energy_density", "wave_direction", "wave_spread"]
        write_csv(dataset.drop_vars(to_drop))

        return dataset

    def hook_plot_dataset(self, dataset: xr.Dataset):
        ds = dataset
        # loc = self.dataset_config.attrs.location_id
        datasetName = self.dataset_config.attrs.dataset_name

        date, time = get_start_date_and_time_str(dataset)

        display = act.plotting.TimeSeriesDisplay(
            ds, subplot_shape=(3,), figsize=(15, 10)
        )

        c1 = amp_r(0.10)
        display.plot(
            "significant_wave_height",
            subplot_index=(0,),
            label="Significant Wave Height",
            color=c1,
        )
        display.axes[0].set_title(
            f"Significant Wave Height for {datasetName} on {date}", pad=-20
        )
        plt.legend()

        c1, c2 = dense(0.15), dense(0.50)
        display.plot("mean_wave_period", subplot_index=(1,), label="Mean Period", color=c1)
        display.plot("peak_wave_period", subplot_index=(1,), label="Peak Period", color=c2)
        display.axes[1].set_title(f"Period for {datasetName} on {date}", pad=-20)
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
        display.axes[2].set_title(
            f"Direction and Directional Spread for {datasetName} on {date}", pad=-20
        )
        plt.legend()

        plt.text(
            1,
            -0.20,
            f"Created using TSDAT {get_code_version()} on {datetime.now(pytz.utc).date()}",
            ha="right",
            va="bottom",
            transform=plt.gca().transAxes,
        )
        plot_file = self.get_ancillary_filepath(title="wave_data_plots")
        plt.savefig(plot_file)  # type: ignore
