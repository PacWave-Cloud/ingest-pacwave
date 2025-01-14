import xarray as xr
from pathlib import Path
from tsdat import PipelineConfig, assert_close


def test_floatr_dat_ctd_pipeline():
    config_path = Path("pipelines/floatr_ctd/config/pipeline_pwn_003.yaml")
    config = PipelineConfig.from_yaml(config_path)
    # Manually set to storage so tests pass
    config.storage.parameters["storage_root"] = "storage"
    pipeline = config.instantiate_pipeline()

    test_file = "pipelines/floatr_ctd/test/data/input/CR1000_PWN_03_IPconnect_Ocean.dat"
    expected_file = "pipelines/floatr_ctd/test/data/expected/pwn.floatr_ctd-003.a1.20220617.000000.nc"

    dataset = pipeline.run([test_file])
    expected: xr.Dataset = xr.open_dataset(expected_file)  # type: ignore
    assert_close(dataset, expected, check_attrs=False)
