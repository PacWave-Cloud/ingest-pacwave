import xarray as xr
from pathlib import Path
from tsdat import PipelineConfig, assert_close


def test_pacwave_pipeline_api_pacwave():
    config_path = Path("pipelines/nexsens/config/pipeline_json.yaml")
    config = PipelineConfig.from_yaml(config_path)
    # Manually set to storage so tests pass
    config.storage.parameters["storage_root"] = "storage"
    pipeline = config.instantiate_pipeline()

    test_file = "pipelines/nexsens/test/input/nexsens-4177.00.20250414.230000.json"
    expected_file = (
        "pipelines/nexsens/test/expected/pws.nexsens-4177.c1.20250414.230000.nc"
    )

    dataset = pipeline.run([test_file])
    expected: xr.Dataset = xr.open_dataset(expected_file)
    assert_close(dataset, expected, check_attrs=False)
