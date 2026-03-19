import xarray as xr
from pathlib import Path
from tsdat import PipelineConfig, assert_close


def test_spotter_raw_pipeline_v3():
    config_path = Path("pipelines/spotter_raw/config/pipeline_30903C.yaml")
    config = PipelineConfig.from_yaml(config_path)
    # Manually set to storage so tests pass
    config.storage.parameters["storage_root"] = "storage"
    pipeline = config.instantiate_pipeline()

    test_file = (
        "pipelines/spotter_raw/test/input/PWS_SPOTTER_30903c_08022024_05152025.zip"
    )
    expected_file = "pipelines/spotter_raw/test/expected/pws.spotter_raw-30903C.a1.20250101.194820.nc"

    dataset = pipeline.run([test_file])
    expected: xr.Dataset = xr.open_dataset(expected_file)  # type: ignore
    assert_close(dataset, expected, check_attrs=False)
