import xarray as xr
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from cmocean.cm import amp_r, dense, haline
from tsdat import IngestPipeline
from mhkit.wave import resource

from shared.misc import set_pacwave_site


class WaveriderWaveStatistics(IngestPipeline):
    """---------------------------------------------------------------------------------
    Pipeline for Waverider wave measurements
    ---------------------------------------------------------------------------------"""

    def hook_customize_dataset(self, dataset: xr.Dataset) -> xr.Dataset:
        # (Optional) Use this hook to modify the dataset before qc is applied
        dataset.attrs.pop("description")

        # Set PacWave location / check if buoys are moved
        dataset = set_pacwave_site(dataset)

        # Set datastream based on CDIP ID #
        if hasattr(dataset, "cdip_station_id"):
            dataset.attrs["qualifier"] = dataset.attrs["cdip_station_id"]
            datastream = dataset.attrs["datastream"].split(".")
            datastream[1] = (
                dataset.attrs["dataset_name"] + "-" + dataset.attrs["qualifier"]
            )
            dataset.attrs["datastream"] = ".".join(datastream)

        # Compute energy period
        dataset["wave_energy_period"].values = resource.energy_period(
            dataset["wave_energy_density"], "frequency", to_pandas=False
        ).values
        # Drop spectral data - users should refer to CDIP server for raw data
        dataset = dataset.drop_vars(("wave_energy_density", "frequency"))

        return dataset

    def hook_finalize_dataset(self, dataset: xr.Dataset) -> xr.Dataset:
        # (Optional) Use this hook to modify the dataset after qc is applied
        # but before it gets saved to the storage area

        to_keep = [
            "qc_latitude",
            "qc_longitude",
            "qc_wave_energy_period",
        ]
        for var in dataset.data_vars:
            # Drop QC vars except for pipeline-specific checks
            if ("qc" in var) and (var not in to_keep):
                dataset = dataset.drop_vars(var)
                continue
            # Don't change these QC variables
            elif var in to_keep:
                continue
            else:
                # Correct ancillary variables for new QC names
                anc_vars = dataset[var].attrs["ancillary_variables"]
                # Drop tsdat-added QC var names from list except for lat/lon
                if var not in ["latitude", "longitude"]:
                    anc_vars = anc_vars.replace(f" qc_{var}", "")
            # Update flag names in list
            if "wave" in anc_vars:
                anc_vars = anc_vars.replace(
                    "waveFlagPrimary", "flag_wave_primary"
                ).replace("waveFlagSecondary", "flag_wave_secondary")
            elif "gps" in anc_vars:
                anc_vars = anc_vars.replace("gpsStatusFlags", "flag_gps")
            elif "sst" in anc_vars:
                anc_vars = anc_vars.replace(
                    "sstFlagPrimary", "flag_sst_primary"
                ).replace("sstFlagSecondary", "flag_sst_secondary")
            dataset[var].attrs["ancillary_variables"] = anc_vars

        return dataset

    def hook_plot_dataset(self, dataset: xr.Dataset):
        # (Optional, recommended) Create plots.
        plt.style.use("default")  # clear any styles that were set before

        fig, ax = plt.subplots(4, 1, figsize=(11, 7), constrained_layout=True)
        c1 = amp_r(0.10)
        ax[0].plot(
            dataset["time"].values,
            dataset["significant_wave_height"],
            ".-",
            label="Significant Wave Height",
            color=c1,
        )
        ax[0].set(ylabel="Height [m]")

        c1, c2, c3 = dense(0.15), dense(0.50), dense(0.8)
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
        ax[1].plot(
            dataset["time"].values,
            dataset["wave_energy_period"],
            ".-",
            label="Energy Period",
            color=c3,
        )
        ax[1].set(ylabel="Period [s]")

        ax[2].plot(
            dataset["time"].values,
            dataset["peak_wave_direction"],
            ".-",
            label="Peak Direction",
            color=haline(0.10),
        )
        ax[2].set(ylabel="Direction [deg]")

        ax[3].plot(
            dataset["time_sst"].values,
            dataset["sea_surface_temperature"],
            ".-",
            label="Sea Surface Temperature",
            color="black",
        )
        ax[3].set(ylabel="Temperature\n[deg C]")

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
