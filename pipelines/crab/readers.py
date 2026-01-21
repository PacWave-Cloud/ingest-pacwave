from pathlib import Path
from typing import Dict, Union
from pydantic import BaseModel, Extra
from datetime import datetime
import numpy as np
import pandas as pd
import xarray as xr
from tsdat import DataReader
from mhkit import acoustics


class WisprReader(DataReader):
    """---------------------------------------------------------------------------------
    Custom DataReader for WISPR acoustic data files.
    ---------------------------------------------------------------------------------"""

    class Parameters(BaseModel, extra=Extra.forbid):
        """If your CustomDataReader should take any additional arguments from the
        retriever configuration file, then those should be specified here.
        """

        bin_length: int = 30  # seconds
        fmin: int = 7  # Hz
        fmax: int = 20000  # Hz
        inst: str = "peri-1"  # Instrument name for calibration file selection

    parameters: Parameters = Parameters()

    def read_24bit_data(self, filename, is_signed=True, endian="<"):
        """
        Reads 24-bit data from a binary file into a 32-bit NumPy array.

        Args:
            filename (str): The path to the binary file.
            is_signed (bool): True if the data is signed 24-bit PCM, False if unsigned.
            endian (str): Byte order, '<' for little-endian, '>' for big-endian.

        Returns:
            np.ndarray: A 32-bit integer NumPy array containing the data.
        """
        # Read the raw data as bytes
        with open(filename, "rb") as f:
            raw_bytes = f.read()

        # Ensure the file size is a multiple of 3 bytes
        if len(raw_bytes) % 3 != 0:
            raise ValueError("File size is not a multiple of 3 bytes (24 bits)")

        # Convert raw bytes into a 1D numpy array of 8-bit integers (uint8)
        data_int8 = np.frombuffer(raw_bytes, dtype=np.uint8)

        # Reshape the 8-bit array into N rows of 3 bytes each
        data_3bytes = data_int8.reshape(-1, 3)

        # Create an empty array to hold the final 32-bit integers
        # Use the appropriate dtype based on 'is_signed'
        dtype_str = f"{endian}i4" if is_signed else f"{endian}u4"
        data_int32 = np.zeros(len(data_3bytes), dtype=dtype_str)

        # Use vectorized slicing to copy the 3 bytes into the lower 3 bytes of the 32-bit array
        data_int32.view(np.uint8)[:, :3] = data_3bytes

        # Handle signed data sign extension if necessary
        if is_signed and endian == "<":
            # If little-endian and the original 24-bit number was negative, the
            # most significant byte (index 2) will have the sign bit set.
            # We correct this by shifting and logical ORing.
            data_int32 = (data_int32 << 8) >> 8

        return data_int32

    def read_wispr(self, file_path):
        """
        Read WISPR .dat file and return xarray DataArray with voltage time series.

        Args:
            file_path (str): Path to WISPR .dat file.

        Returns:
            xr.DataArray: DataArray containing voltage time series and metadata.
        """
        # Read metadata off wispr file header and store in dictionary
        metadata = {}
        with open(file_path, "rb") as f:
            for row in f.readlines():
                try:
                    row = row.decode().strip().split("=")
                except UnicodeDecodeError:
                    break
                if len(row) == 2:
                    key, value = row
                    if "'" in value:
                        value = value.replace("'", "")
                        dtype = str
                    else:
                        dtype = np.float32
                    metadata[key.strip()] = dtype(value.strip().rstrip(";"))
                elif "WISPR" in row[0]:
                    metadata["wispr_version"] = row[0].split(" ")[-1]

        # Clean up metadata
        start_time = np.datetime64(
            datetime.strptime(metadata["time"], "%m:%d:%y:%H:%M:%S")
        )
        fs = int(metadata["sampling_rate"])
        peak_voltage = int(metadata["adc_vref"])
        bits_per_sample = int(metadata["sample_size"] * 8)
        metadata["file_length_sec"] = (
            metadata["file_size"] * 512 / metadata["sample_size"] / fs
        )

        # Read binary data from wispr file
        # Data was recorded in 24-bit by the ADC, saved in 32-bit format by the microcontroller,
        # and finally converted to 16-bit within the WISPR code before being written to file.
        with open(file_path, "rb") as f:
            # skip header lines
            f.seek(512)
            # read binary data (datatype determined by bits per sample)
            if bits_per_sample == 24:
                # 24-bit data is stored as 24-bit signed integers in little-endian format
                data = self.read_24bit_data(file_path, is_signed=True, endian="<")
            else:
                data = np.fromfile(f, dtype=np.int16, offset=0)

        # Normalize and then scale to peak voltage
        max_count = 2 ** (bits_per_sample - 1)
        # Use 64 bit float for decimal accuracy
        raw_voltage = data.astype(float) / max_count * peak_voltage

        # Set time
        end_time = np.datetime64(start_time) + np.timedelta64(
            int(metadata["file_length_sec"] * 1000), "ms"
        )
        time = pd.date_range(start_time, end_time, data.size + 1)

        out = xr.DataArray(
            raw_voltage,
            coords={"time": time[:-1]},
            attrs={
                "units": "V",
                # Voltage min resolution
                "resolution": np.round(peak_voltage / max_count, 9),
                # Minimum voltage sensor can read
                "valid_min": -peak_voltage,
                # Voltage at which sensor is saturated
                "valid_max": peak_voltage,
                "fs": fs,
                "gain": int(metadata["gain"]),
                "filename": Path(file_path).stem,
                "file_length_sec": metadata["file_length_sec"],
                "hdw_version": metadata["wispr_version"],
                "sfw_version": metadata["version"],
                "instrument_id": metadata["instrument_id"],
                "location_id": metadata["location_id"],
            },
        )
        return out

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
        wispr_data = self.read_wispr(input_key)

        # Files are (usually) approximately 5 minutes and we want 30 second averages
        n_bins = wispr_data.file_length_sec / self.parameters.bin_length
        l_bin = np.round(wispr_data.file_length_sec / np.ceil(n_bins), 2)
        # Compute RMS SPSDs
        spsd = acoustics.sound_pressure_spectral_density(
            wispr_data, fs=wispr_data.fs, bin_length=l_bin, fft_length=wispr_data.fs
        )

        # Read sensitivity curve file
        sensitivity_curve = self.set_sensitivity_curve(input_key)
        # Apply gain (usually 0) and preamp factor (usually 6 dB)
        sensitivity_curve += wispr_data.gain * 6
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
        ds.attrs["hdw_version"] = wispr_data.hdw_version
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
