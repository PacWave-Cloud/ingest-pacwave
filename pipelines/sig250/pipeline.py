from pathlib import Path
import pandas as pd
import xarray as xr
import matplotlib.pyplot as plt
from mhkit import dolfyn
from tsdat import IngestPipeline


def calc_declination(time):
    # Estimate declination by current change of 0.01 deg W per year
    t = pd.Timestamp(time[0].values)
    day_of_year = t.timetuple().tm_yday
    declin = 14.83 - (t.year - 2024 + day_of_year / 365.25) * 0.09

    return declin


class UpLookingSig250(IngestPipeline):
    def hook_customize_dataset(self, dataset: xr.Dataset) -> xr.Dataset:
        # (Optional) Use this hook to modify the dataset before qc is applied

        filename = Path(dataset.inputs).stem
        qualifier = filename.split("_")[-1]
        dataset.attrs["qualifier"] = "0" + qualifier
        dataset.attrs["datastream"] = dataset.attrs["datastream"].replace(
            "001", "0" + qualifier
        )

        # Correct magnetic declination
        declin = calc_declination(dataset["time"])
        dolfyn.set_declination(dataset, declin, inplace=True)  # 14.8 deg East
        dolfyn.rotate2(dataset, "earth")

        return dataset

    def hook_finalize_dataset(self, dataset: xr.Dataset) -> xr.Dataset:
        # (Optional) Use this hook to modify the dataset after qc is applied
        # but before it gets saved to the storage area

        return dataset

    def hook_plot_dataset(self, ds: xr.Dataset):
        with plt.style.context("shared/styling.mplstyle"):
            # Plot surface
            fig, ax = plt.subplots(1, figsize=(10, 7), constrained_layout=True)
            ds["ast_dist_alt"].plot(label="Altimeter AST")
            ds["le_dist_alt"].plot(label="Altimeter LE")
            ds["depth"].plot(label="Depth")
            plt.legend()
            plt.ylabel("Range [m]")

            plot_file = self.get_ancillary_filepath(title="surface")
            fig.savefig(plot_file)
            plt.close(fig)

            # Plot CTD
            fig, ax = plt.subplots(3, figsize=(10, 7), constrained_layout=True)

            ax[0].plot(ds["time"].values, ds["depth"])
            ax[0].set(xlabel="Time", ylabel="Instrument Depth [m]")

            ax[1].plot(ds["time"].values, ds["temperature"])
            ax[1].set(xlabel="Time", ylabel="Water Temperature [C]")

            ax[2].plot(ds["time"].values, ds["speed_of_sound"])
            ax[2].set(xlabel="Time", ylabel="Speed of Sound [m/s]")

            plot_file = self.get_ancillary_filepath(title="environment")
            fig.savefig(plot_file)
            plt.close(fig)
