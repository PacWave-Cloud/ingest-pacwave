import xarray as xr

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import tsdat
from tsdat import TransformationPipeline, get_start_date_and_time_str, get_code_version
import act
from cmocean.cm import amp_r, dense, haline
import pytz
from datetime import datetime, timedelta
import numpy as np


# DEVELOPER: Implement your pipeline and update its docstring.
class VapPacwave(TransformationPipeline):
    """---------------------------------------------------------------------------------
    This is an example pipeline meant to demonstrate how one might set up a
    pipeline using this template repository.

    ---------------------------------------------------------------------------------"""

    def hook_customize_dataset(self, dataset: xr.Dataset) -> xr.Dataset:
        # DEVELOPER: (Optional) Use this hook to modify the dataset before qc is applied
        return dataset

    def hook_finalize_dataset(self, dataset: xr.Dataset) -> xr.Dataset:
        # DEVELOPER: (Optional) Use this hook to modify the dataset after qc is applied
        # but before it gets saved to the storage area
        return dataset

    def hook_plot_dataset(self, dataset: xr.Dataset):
        # DEVELOPER: (Optional, recommended) Create plots.

        # date, time = get_start_date_and_time_str(dataset)

        location = self.dataset_config.attrs.location_id
        datastream: str = self.dataset_config.attrs.datastream
        date, time = get_start_date_and_time_str(dataset)

        min_date = dataset["time"].min().values
        start_date = np.datetime_as_string(min_date, unit="D")
        max_date = dataset["time"].max().values
        end_date = np.datetime_as_string(max_date, unit="D")
        filename_end_date = datetime.utcfromtimestamp(
            np.datetime64(max_date).astype(int) * 1e-9
        ).strftime("%Y%m%d")

        save_kwargs = {
            "root_dir": "storage/root",
            "location_id": location,
            "datastream": datastream,
            "year": date[:4],
            "month": date[4:6],
            "day": date[6:],
        }

        date, time = get_start_date_and_time_str(dataset)

        display = act.plotting.TimeSeriesDisplay(
            dataset, subplot_shape=(3,), figsize=(15, 10)
        )

        c1 = amp_r(0.10)
        display.plot(
            "significantWaveHeight",
            subplot_index=(0,),
            label="Significant Wave Height",
            color=c1,
        )
        display.axes[0].xaxis.set_major_locator(mdates.DayLocator(interval=5))
        display.axes[0].xaxis.set_major_formatter(mdates.DateFormatter("%b%d"))
        display.axes[0].set_title(
            f"Significant Wave Height for {datastream} from {start_date} to {end_date}",
            pad=-20,
        )

        c1, c2 = dense(0.15), dense(0.50)
        display.plot("meanPeriod", subplot_index=(1,), label="Mean Period", color=c1)
        display.plot("peakPeriod", subplot_index=(1,), label="Peak Period", color=c2)
        display.axes[1].xaxis.set_major_locator(mdates.DayLocator(interval=5))
        display.axes[1].xaxis.set_major_formatter(mdates.DateFormatter("%b%d"))
        display.axes[1].set_title(
            f"Period for {datastream} from {start_date} to {end_date}", pad=-20
        )
        plt.legend()

        c1, c2, c3, c4 = haline(0.10), haline(0.30), haline(0.50), haline(0.70)
        display.plot(
            "peakDirection", subplot_index=(2,), label="Peak Direction", color=c1
        )
        display.plot(
            "meanDirection", subplot_index=(2,), label="Mean Direction", color=c2
        )
        display.plot(
            "peakDirectionalSpread",
            subplot_index=(2,),
            label="Peak Directional Spread",
            color=c3,
        )
        display.plot(
            "meanDirectionalSpread",
            subplot_index=(2,),
            label="Mean Directional Spread",
            color=c4,
        )
        display.axes[2].xaxis.set_major_locator(mdates.DayLocator(interval=5))
        display.axes[2].xaxis.set_major_formatter(mdates.DateFormatter("%b%d"))
        display.axes[2].set_title(
            f"Direction and Directional Spread for {datastream} from {start_date} to {end_date}",
            pad=-20,
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

        plot_file = self.get_ancillary_filepath(
            title=f"{filename_end_date}.wave_data_plot", **save_kwargs
        )
        plt.savefig(plot_file)
        return dataset
