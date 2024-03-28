import xarray as xr
from pathlib import Path
from tsdat import PipelineConfig, assert_close


def test_pacwave_pipeline():
    config_path = Path("pipelines/spotter/config/pipeline_30897C.yaml")
    config = PipelineConfig.from_yaml(config_path)
    pipeline = config.instantiate_pipeline()

    test_file = (
        "pipelines/spotter/test/input/SPOT-30897C_2024-02-29_2024-03-02_download.csv"
    )
    expected_file = (
        "pipelines/spotter/test/expected/pwn.spot_30897c.c1.20240229.170000.nc"
    )

    dataset = pipeline.run([test_file])
    expected: xr.Dataset = xr.open_dataset(expected_file)
    assert_close(dataset, expected, check_attrs=False)
