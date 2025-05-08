import requests
import json
from pathlib import Path


def set_floatr_buoy_number(dataset):
    """
    Retrieves the buoy number from the second position
    in the filename and sets the qualifer and dataset attributes.
    """
    filename = Path(dataset.inputs).stem
    qualifier = filename.split("_")[1]
    dataset.attrs["qualifier"] = qualifier
    dataset.attrs["datastream"] = dataset.attrs["datastream"].replace("001", qualifier)
    return dataset


def set_pacwave_site(dataset):
    """
    Looks at the latitude and longitude readings in the dataset to
    determine whether in the buoy was located in PacWave North or
    PacWave South.

    PacWave South Bounds:
    NW: 44º 35' 00.00” N, 124º 14' 30.00” W
    NE: 44º 35' 02.75” N, 124º 13' 06.17” W
    SE: 44º 33' 02.75” N, 124º 12' 58.51” W
    SW: 44º 33' 00.00” N, 124º 14' 22.41” W

    PacWave North Bounds:
    NW: 44º 41' 52.08” N, 124º 08' 46.32” W
    NE: 44º 41' 54.96” N, 124º 07' 22.44” W
    SE: 44º 40' 54.84” N, 124º 07' 18.48” W
    SW: 44º 40' 52.32” N, 124º 08' 42.72” W
    """

    pwn_bounds = {"N": 44.6986, "S": 44.6812, "W": -124.1462, "E": -124.1218}
    pws_bounds = {"N": 44.5841, "S": 44.5500, "W": -124.2417, "E": -124.2163}

    lat = dataset["latitude"].dropna("time")
    lat_pwn = (lat > pwn_bounds["S"]) & (lat < pwn_bounds["N"])
    lat_pws = (lat > pws_bounds["S"]) & (lat < pws_bounds["N"])

    lon = dataset["longitude"].dropna("time")
    lon_pwn = (lon > pwn_bounds["W"]) & (lon < pwn_bounds["E"])
    lon_pws = (lon > pws_bounds["W"]) & (lon < pws_bounds["E"])

    total_pwn = (lat_pwn + lon_pwn).sum()
    total_pws = (lat_pws + lon_pws).sum()

    datastream = dataset.attrs["datastream"].split(".")
    if total_pwn > total_pws:
        dataset.attrs["location_id"] = "pwn"
        datastream[0] = "pwn"
        dataset.attrs["geospatial_lat_min"] = pwn_bounds["S"]
        dataset.attrs["geospatial_lat_max"] = pwn_bounds["N"]
        dataset.attrs["geospatial_lon_min"] = pwn_bounds["W"]
        dataset.attrs["geospatial_lon_max"] = pwn_bounds["E"]
    else:
        dataset.attrs["location_id"] = "pws"
        datastream[0] = "pws"
        dataset.attrs["geospatial_lat_min"] = pws_bounds["S"]
        dataset.attrs["geospatial_lat_max"] = pws_bounds["N"]
        dataset.attrs["geospatial_lon_min"] = pws_bounds["W"]
        dataset.attrs["geospatial_lon_max"] = pws_bounds["E"]
    dataset.attrs["datastream"] = ".".join(datastream)

    return dataset


def request_spotter_data(spotter, start_date, end_date, token):
    # Request requires that spotter belongs to the user (token)
    url = "https://api.sofarocean.com/api/wave-data?"
    payload = {
        "spotterId": spotter,
        "startDate": start_date,
        "endDate": end_date,
        "includeWaves": "true",
        "includeSurfaceTempData": "true",
        "includeTrack": "false",  # Included in waves data
        "includeFrequencyData": "true",
        "includeDirectionalMoments": "true",
        "includePartitionData": "true",
        "includeBarometerData": "true",
    }
    headers = {"token": token}
    res = requests.get(url, params=payload, headers=headers)

    data = res.json()
    filename = (
        spotter.lower() + "." + start_date.replace("-", "").replace(":", "") + ".json"
    )
    with open(filename, "w") as f:
        json.dump(data, f)

    return filename


def request_nexsens_data(nexsens, token):
    # Request requires that nexsens belongs to the user (token) Your NexSens API Key
    device_id = nexsens
    url = f"https://www.wqdatalive.com/api/v1/devices/{device_id}/parameters/data/latest?apiKey={token}"
    res = requests.get(url)

    data = res.json()
    filename = nexsens.lower() + ".json"
    with open("data.json", "w") as f:
        json.dump(data, f)

    return filename
