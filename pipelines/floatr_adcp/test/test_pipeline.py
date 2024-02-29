import xarray as xr
from pathlib import Path
from tsdat import PipelineConfig, assert_close


def test_floatr_dat_adcp_pipeline():
    config_path = Path("pipelines/floatr_adcp/config/pipeline_pws.yaml")
    config = PipelineConfig.from_yaml(config_path)
    pipeline = config.instantiate_pipeline()

    test_file = "pipelines/floatr_adcp/test/data/input/PWS_001_ADCP.dat"
    expected_file = (
        "pipelines/floatr_adcp/test/data/expected/pws.floatr_adcp.a1.20210816.043000.nc"
    )

    dataset = pipeline.run([test_file])
    expected: xr.Dataset = xr.open_dataset(expected_file)  # type: ignore
    assert_close(dataset, expected, check_attrs=False)


def test_floatr_000_adcp_pipeline():
    config_path = Path("pipelines/floatr_adcp/config/pipeline_000.yaml")
    config = PipelineConfig.from_yaml(config_path)
    pipeline = config.instantiate_pipeline()

    test_file = "pipelines/floatr_adcp/test/data/input/AUG21003.000"
    expected_file = "pipelines/floatr_adcp/test/data/expected/pws.floatr_adcp-000.b1.20210812.233000.nc"

    dataset = pipeline.run([test_file])
    expected: xr.Dataset = xr.open_dataset(expected_file)  # type: ignore
    assert_close(dataset, expected, check_attrs=False)
