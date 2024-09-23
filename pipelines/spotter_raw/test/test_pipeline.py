import xarray as xr
from pathlib import Path
from tsdat import PipelineConfig, assert_close


def test_waves_pipeline():
    config_path = Path("pipelines/spotter_raw/config/pipeline_flt.yaml")
    config = PipelineConfig.from_yaml(config_path)
    pipeline = config.instantiate_pipeline()

    test_file = "pipelines/spotter_raw/test/data/input/0026_FLT.CSV"
    expected_file = "pipelines/spotter_raw/test/data/expected/pwn.spotter-pos-400ms.a1.20210903.160801.nc"

    dataset = pipeline.run([test_file])
    expected: xr.Dataset = xr.open_dataset(expected_file)  # type: ignore
    assert_close(dataset, expected, check_attrs=False)


def test_gps_pipeline():
    config_path = Path("pipelines/spotter_raw/config/pipeline_loc.yaml")
    config = PipelineConfig.from_yaml(config_path)
    pipeline = config.instantiate_pipeline()

    test_file = "pipelines/spotter_raw/test/data/input/0026_LOC.CSV"
    expected_file = "pipelines/spotter_raw/test/data/expected/pwn.spotter-gps-1min.a1.20210903.160821.nc"

    dataset = pipeline.run([test_file])
    expected: xr.Dataset = xr.open_dataset(expected_file)  # type: ignore
    assert_close(dataset, expected, check_attrs=False)


def test_sst_pipeline():
    config_path = Path("pipelines/spotter_raw/config/pipeline_sst.yaml")
    config = PipelineConfig.from_yaml(config_path)
    pipeline = config.instantiate_pipeline()

    test_file = "pipelines/spotter_raw/test/data/input/0026_SST.CSV"
    expected_file = "pipelines/spotter_raw/test/data/expected/pwn.spotter-sst-1min.a1.20210903.160822.nc"

    dataset = pipeline.run([test_file])
    expected: xr.Dataset = xr.open_dataset(expected_file)  # type: ignore
    assert_close(dataset, expected, check_attrs=False)
