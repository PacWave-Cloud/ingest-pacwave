import xarray as xr
import matplotlib.pyplot as plt
from tsdat import IngestPipeline
from mhkit import acoustics
from shared.writers import write_csv


class PacwaveCrabHydrophones(IngestPipeline):
    def hook_customize_dataset(self, dataset: xr.Dataset) -> xr.Dataset:
        # (Optional) Use this hook to modify the dataset before qc is applied
        return dataset

    def hook_finalize_dataset(self, dataset: xr.Dataset) -> xr.Dataset:
        # (Optional) Use this hook to modify the dataset after qc is applied
        # but before it gets saved to the storage area

        # Save csv file
        write_csv(dataset)

        return dataset

    def hook_plot_dataset(self, dataset: xr.Dataset):
        # (Optional, recommended) Create plots.

        # with plt.style.context("shared/styling.mplstyle"):
        #     kwargs = {"cmap": "inferno", "vmin": 20, "vmax": 120}
        #     fig, ax = acoustics.graphics.plot_spectrogram(
        #         dataset["spsdl"],
        #         fmin=dataset["spl"].freq_band_min,
        #         fmax=dataset["spl"].freq_band_max,
        #         **kwargs,
        #     )
        #     plot_filepath = self.get_ancillary_filepath(title="spectrogram")
        #     fig.savefig(plot_filepath)
        #     plt.close(fig)

        #     fig, ax = acoustics.graphics.plot_spectra(
        #         dataset["spsdl"].median("time"),
        #         dataset["spl"].freq_band_min,
        #         dataset["spl"].freq_band_max,
        #     )
        #     ax.fill_between(
        #         dataset["freq"],
        #         dataset["spsdl"].quantile(0.75, "time"),
        #         dataset["spsdl"].quantile(0.25, "time"),
        #         alpha=0.3,
        #     )
        #     ax.set(ylim=(20, 100), ylabel="Median SPSDL (dB re 1 µPa²/Hz)")
        #     plot_filepath = self.get_ancillary_filepath(title="spsdl")
        #     fig.savefig(plot_filepath)
        #     plt.close(fig)

        pass
