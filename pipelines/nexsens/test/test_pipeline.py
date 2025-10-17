import xarray as xr
from pathlib import Path
from tsdat import PipelineConfig, assert_close


def test_pacwave_pipeline_api_pacwave():
    config_path = Path("pipelines/nexsens/config/pipeline_json.yaml")
    config = PipelineConfig.from_yaml(config_path)
    # Manually set to storage so tests pass
    config.storage.parameters["storage_root"] = "storage"
    pipeline = config.instantiate_pipeline()

    test_file = "pipelines/nexsens/test/input/4844.00.20251014T000000.json"
    expected_file = (
        "pipelines/nexsens/test/expected/pws.nexsens-4844.c1.20251014.000000.nc"
    )

    dataset = pipeline.run([test_file])
    expected: xr.Dataset = xr.open_dataset(expected_file)
    assert_close(dataset, expected, check_attrs=False)
