import xarray as xr
from pathlib import Path
from tsdat import PipelineConfig, assert_close


def test_waverider_pipeline():
    config_path = Path("pipelines/waverider/config/pipeline.yaml")
    config = PipelineConfig.from_yaml(config_path)
    # Manually set to storage so tests pass
    config.storage.parameters["storage_root"] = "storage"
    pipeline = config.instantiate_pipeline()
    test_file = "pipelines/waverider/test/data/input/280p1_rt.nc"
    expected_file = (
        "pipelines/waverider/test/data/expected/pws.waverider-280.c1.20250801.190000.nc"
    )

    dataset = pipeline.run([test_file])
    expected: xr.Dataset = xr.open_dataset(expected_file)  # type: ignore
    assert_close(dataset, expected, check_attrs=False)
