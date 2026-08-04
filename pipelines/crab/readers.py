from pathlib import Path
from typing import Dict, Union
from pydantic import BaseModel
from datetime import datetime
import numpy as np
import pandas as pd
import xarray as xr
from tsdat import DataReader
from mhkit import acoustics
from mhkit.acoustics.io import read_wispr


class WisprReader(DataReader):
    """---------------------------------------------------------------------------------
    Custom DataReader for WISPR acoustic data files.
    ---------------------------------------------------------------------------------"""

    class Parameters(BaseModel):
        """If your CustomDataReader should take any additional arguments from the
        retriever configuration file, then those should be specified here.
        """

        bin_length: int = 30  # seconds
        fmin: int = 7  # Hz
        fmax: int = 5000  # Hz
        inst: str = "crab"  # Instrument name for calibration file selection

    parameters: Parameters = Parameters()

    def set_sensitivity_curve(self, filepath: str) -> xr.DataArray:
        """Set sensitivity curve from calibration file.

        Args:
            filepath (str): Path to WISPR .dat file.

        Returns:
            xr.DataArray: DataArray containing sensitivity curve.
        """
        # Determine calibration file based on year in filename
        year = int(Path(filepath).stem.split("_")[1][0:2])
        # Use calibration file for closest or latest year available
        inst = self.parameters.inst
        while not Path(f"pipelines/crab/calibration/{inst}.20{year}.csv").is_file():
            year += 1
            if year > (datetime.now().year % 100):
                while not Path(
                    f"pipelines/crab/calibration/{inst}.20{year}.csv"
                ).is_file():
                    year -= 1
                    if year < 20:
                        raise FileNotFoundError(
                            "No calibration file found for instrument."
                        )
        # Read file
        sensitivity_curve = pd.read_csv(
            f"pipelines/crab/calibration/{inst}.20{year}.csv", sep=","
        )
        # Set up xarray DataArray
        sensitivity_curve.index = sensitivity_curve["Freq [Hz]"]
        sensitivity_curve = sensitivity_curve.to_xarray()["Sensitivity"]
        return sensitivity_curve

    def read(self, input_key: str) -> Union[xr.Dataset, Dict[str, xr.Dataset]]:
        # Read raw file
        wispr_data = read_wispr(input_key)

        # Compute RMS SPSDs
        l_bin = self.parameters.bin_length
        spsd = acoustics.sound_pressure_spectral_density(
            wispr_data,
            fs=wispr_data.fs,
            bin_length=l_bin,
            fft_length=wispr_data.fs,
            pct_overlap=0.5,
        )

        # Read sensitivity curve file
        sensitivity_curve = self.set_sensitivity_curve(input_key)
        sensitivity_curve = sensitivity_curve + wispr_data.gain
        # Apply calibration curve
        spsd = acoustics.apply_calibration(
            spsd,
            sensitivity_curve,
            fill_value=sensitivity_curve[-1].item(),
            interp_method="pchip",
        )

        # Create dataset
        ds = xr.Dataset()
        ds.attrs["filename"] = wispr_data.filename
        ds.attrs["instrument_id"] = wispr_data.instrument_id
        ds.attrs["location_id"] = wispr_data.location_id
        ds.attrs["sfw_version"] = wispr_data.sfw_version
        ds.attrs["fs"] = wispr_data.fs
        ds.attrs["file_length_sec"] = wispr_data.file_length_sec
        ds.attrs["bin_length_sec"] = l_bin
        # Full spectrograms
        ds["spsdl"] = acoustics.sound_pressure_spectral_density_level(spsd)
        # Full frequency range SPLs
        ds["spl"] = acoustics.sound_pressure_level(
            spsd, self.parameters.fmin, self.parameters.fmax
        )

        return ds
