import xarray as xr
from pathlib import Path
from tsdat import PipelineConfig, assert_close


def test_spotter_raw_pipeline_v3():
    config_path = Path("pipelines/spotter_raw/config/pipeline.yaml")
    config = PipelineConfig.from_yaml(config_path)
    # Manually set to storage so tests pass
    config.storage.parameters["storage_root"] = "storage"
    pipeline = config.instantiate_pipeline()

    test_file = "pipelines/spotter_raw/test/input/spotter.pwn.32563c.202510.nc"
    expected_file = "pipelines/spotter_raw/test/expected/pwn.spotter_raw-32563c.a1.20251001.000000.nc"

    dataset = pipeline.run([test_file])
    expected: xr.Dataset = xr.open_dataset(expected_file)  # type: ignore
    assert_close(dataset, expected, check_attrs=False)
