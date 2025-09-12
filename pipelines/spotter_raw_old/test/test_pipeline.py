import xarray as xr
from pathlib import Path
from tsdat import PipelineConfig, assert_close


def test_spotter_raw_old_pipeline():
    config_path = Path("pipelines/spotter_raw_old/config/pipeline_0486.yaml")
    config = PipelineConfig.from_yaml(config_path)
    # Manually set to storage so tests pass
    config.storage.parameters["storage_root"] = "storage"
    pipeline = config.instantiate_pipeline()

    test_file = "pipelines/spotter_raw_old/test/data/input/PWS_SPOTTER_0486_08022024_05152025.zip"
    expected_file = "pipelines/spotter_raw_old/test/data/expected/pws.spotter-0486.a1.20241228.182131.nc"

    dataset = pipeline.run([test_file])
    expected: xr.Dataset = xr.open_dataset(expected_file)  # type: ignore
    assert_close(dataset, expected, check_attrs=False)
