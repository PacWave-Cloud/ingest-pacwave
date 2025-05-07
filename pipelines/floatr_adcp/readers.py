from typing import Dict, Union
import numpy as np
import pandas as pd
import xarray as xr
from datetime import datetime, time as dtime
from mhkit import dolfyn
from tsdat import DataReader

from pipelines.floatr_adcp_raw.readers import calc_declination


class CampbellRDIReader(DataReader):
    """---------------------------------------------------------------------------------
    Reads RDI ADCP raw data being stored by a Campbell datalogger in FLOATr buoys in
    PacWave.
    ---------------------------------------------------------------------------------"""

    def old_header(self, input_key):
        names = [
            "buffer",
            "year",
            "day",
            "hhmm",
            "second",
            "ADCP_hr",
            "ADCP_min",
            "j_u3LSB",
            "j_u3MSB",
            "j_v3LSB",
            "j_v3MSB",
            "j_u10LSB",
            "j_u10MSB",
            "j_v10LSB",
            "j_v10MSB",
            "j_u18LSB",
            "j_u18MSB",
            "j_v18LSB",
            "j_v18MSB",
            "j_u25LSB",
            "j_u25MSB",
            "j_v25LSB",
            "j_v25MSB",
            "j_u32LSB",
            "j_u32MSB",
            "j_v32LSB",
            "j_v32MSB",
        ]
        csv = pd.read_csv(input_key, sep=",", names=names, na_values=-7999)

        # Make time coordinate
        date = []
        time_log = []
        for i in range(len(csv)):
            datestring = f"{csv['year'][i]}{csv['day'][i]}"
            date.append(datetime.strptime(datestring, "%Y%j"))

            hour = int(str(csv["hhmm"][i]).zfill(4)[:2])
            minute = int(str(csv["hhmm"][i]).zfill(4)[2:])
            time_log.append(dtime(hour, minute, csv["second"][i]))
            time_log[i] = datetime.combine(date[i], time_log[i])

        csv["time"] = dolfyn.time.date2dt64(time_log)
        csv = csv.drop(columns=["year", "day", "hhmm", "second"])
        return csv

    def new_header(self, input_key):
        names = [
            "time",
            "record",
            "adcp_hr",
            "adcp_min",
            "j_u3LSB",
            "j_u3MSB",
            "j_v3LSB",
            "j_v3MSB",
            "j_u10LSB",
            "j_u10MSB",
            "j_v10LSB",
            "j_v10MSB",
            "j_u18LSB",
            "j_u18MSB",
            "j_v18LSB",
            "j_v18MSB",
            "j_u25LSB",
            "j_u25MSB",
            "j_v25LSB",
            "j_v25MSB",
            "j_u32LSB",
            "j_u32MSB",
            "j_v32LSB",
            "j_v32MSB",
        ]
        csv = pd.read_csv(
            input_key,
            sep=",",
            names=names,
            skiprows=4,
            na_values="NAN",
            engine="python",
        )
        return csv

    def rebuild_adcp_vel(self, MSB, LSB):
        """Reconstruct a signed integer out of RDI's byte values
        MSB is the most significant byte
        LSB is the least significant byte
        output is in mm/s converted to m/s
        """

        vmmps = 256 * MSB + LSB  # vmmps is the two's complement of the velocity
        nan_mask = vmmps.isnull().values

        out = np.array(vmmps, np.int16).astype(np.float32) / 1000
        out[nan_mask] = np.nan

        return out

    def read(self, input_key: str) -> Union[xr.Dataset, Dict[str, xr.Dataset]]:
        # Read csv file
        try:
            csv = self.old_header(input_key)
        except ValueError:
            csv = self.new_header(input_key)

        if not csv.dropna().size:
            raise EOFError("No data found in file.")

        # Create velocity profiles
        ranges = [3, 10, 18, 25, 32]
        enu = ["u", "v"]
        vel = np.zeros((len(csv), len(ranges), len(enu)))
        for i, u in enumerate(enu):
            for j, r in enumerate(ranges):
                msb = "j_" + u + str(r) + "MSB"
                lsb = "j_" + u + str(r) + "LSB"
                vel[:, j, i] = self.rebuild_adcp_vel(csv[msb], csv[lsb])

        # Velocity data has been rotated properly by the ADCP given an
        # "up" or "down" orientation before sending to satellite, even if
        # orientation is improperly recorded in the raw file.
        vel = xr.DataArray(
            vel,
            coords={
                "time": csv["time"].astype("datetime64[ns]"),
                "range": ranges,
                "dir": enu,
            },
        )
        # drop fully nan data
        vel = vel.where(~vel.isnull(), drop=True)

        # Set magnetic declination
        declin = calc_declination(vel["time"])
        rot = np.array(
            [[np.cos(declin), -np.sin(declin)], [np.sin(declin), np.cos(declin)]]
        )
        # transpose to match u & v axes correctly
        vel.values = np.einsum("ij,j...->i...", rot, vel.T).T

        ds = xr.Dataset()
        ds["vel_east"] = vel[..., 0]  # u
        ds["vel_north"] = vel[..., 1]  # v

        return ds
