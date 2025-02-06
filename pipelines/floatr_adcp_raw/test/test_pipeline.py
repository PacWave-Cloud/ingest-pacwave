import xarray as xr
from pathlib import Path
from tsdat import PipelineConfig, assert_close


def test_floatr_raw_adcp_pipeline():
    config_path = Path("pipelines/floatr_adcp_raw/config/pipeline_pws_003.yaml")
    config = PipelineConfig.from_yaml(config_path)
    # Manually set to storage so tests pass
    config.storage.parameters["storage_root"] = "storage"
    pipeline = config.instantiate_pipeline()

    test_file = "pipelines/floatr_adcp_raw/test/data/input/AUG21003.000"
    expected_file = "pipelines/floatr_adcp_raw/test/data/expected/pws.floatr_adcp_raw-003.a1.20210812.233000.nc"

    dataset = pipeline.run([test_file])
    expected: xr.Dataset = xr.open_dataset(expected_file)  # type: ignore
    assert_close(dataset, expected, check_attrs=False)
