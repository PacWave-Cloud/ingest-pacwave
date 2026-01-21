import xarray as xr
from pathlib import Path
from tsdat import PipelineConfig, assert_close


def test_crab_pipeline():
    config_path = Path("pipelines/crab/config/pipeline_pws.yaml")
    config = PipelineConfig.from_yaml(config_path)
    # Manually set to storage so tests pass
    config.storage.parameters["storage_root"] = "storage"
    pipeline = config.instantiate_pipeline()

    test_file = "pipelines/crab/test/data/input/WISPR_240910_042317.dat"
    expected_file = "pipelines/crab/test/data/expected/pws.crab-1.a0.20240910.042328.nc"

    dataset = pipeline.run([test_file])
    expected: xr.Dataset = xr.open_dataset(expected_file)  # type: ignore
    assert_close(dataset, expected, check_attrs=False)
