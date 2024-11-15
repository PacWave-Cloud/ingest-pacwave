import xarray as xr
from pathlib import Path
from tsdat import PipelineConfig, assert_close


def test_floatr_dat_met_pipeline():
    config_path = Path("pipelines/floatr_met/config/pipeline_pws_002.yaml")
    config = PipelineConfig.from_yaml(config_path)
    # Manually set to storage so tests pass
    config.storage.parameters["storage_root"] = "storage"
    pipeline = config.instantiate_pipeline()

    test_file = "pipelines/floatr_met/test/data/input/CR1000x_PWS_002_IPconnect_Met.dat"
    expected_file = (
        "pipelines/floatr_met/test/data/expected/pws.floatr_met-002.a1.20220307.160000.nc"
    )

    dataset = pipeline.run([test_file])
    expected: xr.Dataset = xr.open_dataset(expected_file)  # type: ignore
    assert_close(dataset, expected, check_attrs=False)
