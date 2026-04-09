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
        #     fig, ax = acoustics.graphics.plot_spectra(
        #         dataset["spsdl"].mean("time"),
        #         dataset["spl"].freq_band_min,
        #         dataset["spl"].freq_band_max,
        #     )
        #     ax.set(ylim=(40, 140), ylabel="Median SPSDL (dB re 1 µPa²/Hz)")
        #     plot_filepath = self.get_ancillary_filepath(title="spsdl")
        #     fig.savefig(plot_filepath)
        #     plt.close(fig)

        pass
