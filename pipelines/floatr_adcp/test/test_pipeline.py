import xarray as xr
from pathlib import Path
from tsdat import PipelineConfig, assert_close


def test_floatr_dat_adcp_pipeline_old():
    config_path = Path("pipelines/floatr_adcp/config/pipeline.yaml")
    config = PipelineConfig.from_yaml(config_path)
    # Manually set to storage so tests pass
    config.storage.parameters["storage_root"] = "storage"
    pipeline = config.instantiate_pipeline()

    test_file = "pipelines/floatr_adcp/test/data/input/PWS_001_ADCP.dat"
    expected_file = "pipelines/floatr_adcp/test/data/expected/pws.floatr_adcp-001.a1.20210812.234000.nc"

    dataset = pipeline.run([test_file])
    expected: xr.Dataset = xr.open_dataset(expected_file)  # type: ignore
    assert_close(dataset, expected, check_attrs=False)


def test_floatr_dat_adcp_pipeline():
    config_path = Path("pipelines/floatr_adcp/config/pipeline_pws_003.yaml")
    config = PipelineConfig.from_yaml(config_path)
    # Manually set to storage so tests pass
    config.storage.parameters["storage_root"] = "storage"
    pipeline = config.instantiate_pipeline()

    test_file = "pipelines/floatr_adcp/test/data/input/PWS_003_ADCP.dat"
    expected_file = "pipelines/floatr_adcp/test/data/expected/pws.floatr_adcp-003.a1.20230325.215000.nc"

    dataset = pipeline.run([test_file])
    expected: xr.Dataset = xr.open_dataset(expected_file)  # type: ignore
    assert_close(dataset, expected, check_attrs=False)
