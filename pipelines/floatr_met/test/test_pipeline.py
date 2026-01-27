import xarray as xr
from pathlib import Path
from tsdat import PipelineConfig, assert_close


def test_floatr_dat_met_pipeline_pws007():
    config_path = Path("pipelines/floatr_met/config/pipeline_pws.yaml")
    config = PipelineConfig.from_yaml(config_path)
    # Manually set to storage so tests pass
    config.storage.parameters["storage_root"] = "storage"
    pipeline = config.instantiate_pipeline()

    test_file = "pipelines/floatr_met/test/data/input/PWS_007_met.20250723.220000.dat"
    expected_file = "pipelines/floatr_met/test/data/expected/pws.floatr_met-007.a1.20250723.220000.nc"

    dataset = pipeline.run([test_file])
    expected: xr.Dataset = xr.open_dataset(expected_file)  # type: ignore
    assert_close(dataset, expected, check_attrs=False)


def test_floatr_dat_met_pipeline_pwn003():
    config_path = Path("pipelines/floatr_met/config/pipeline_pwn.yaml")
    config = PipelineConfig.from_yaml(config_path)
    # Manually set to storage so tests pass
    config.storage.parameters["storage_root"] = "storage"
    pipeline = config.instantiate_pipeline()

    test_file = "pipelines/floatr_met/test/data/input/PWN_003_Met.20230703.000000.dat"
    expected_file = "pipelines/floatr_met/test/data/expected/pwn.floatr_met-003.a1.20230703.000000.nc"

    dataset = pipeline.run([test_file])
    expected: xr.Dataset = xr.open_dataset(expected_file)  # type: ignore
    assert_close(dataset, expected, check_attrs=False)
