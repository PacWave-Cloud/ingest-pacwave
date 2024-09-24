import xarray as xr
from pathlib import Path
from tsdat import PipelineConfig, assert_close


def test_pacwave_pipeline_csv():
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


def test_pacwave_pipeline_api_rtd():
    config_path = Path("pipelines/spotter/config/pipeline.yaml")
    config = PipelineConfig.from_yaml(config_path)
    pipeline = config.instantiate_pipeline()

    test_file = "pipelines/spotter/test/input/data.json"
    expected_file = (
        "pipelines/spotter/test/expected/pws.spot_0401.c1.20210901.002528.nc"
    )

    dataset = pipeline.run([test_file])
    expected: xr.Dataset = xr.open_dataset(expected_file)
    assert_close(dataset, expected, check_attrs=False)


def test_pacwave_pipeline_api_sample():
    config_path = Path("pipelines/spotter/config/pipeline.yaml")
    config = PipelineConfig.from_yaml(config_path)
    pipeline = config.instantiate_pipeline()

    test_file = "pipelines/spotter/test/input/sample.json"
    expected_file = (
        "pipelines/spotter/test/expected/pws.spot_0401.c1.20171012.132840.nc"
    )

    dataset = pipeline.run([test_file])
    expected: xr.Dataset = xr.open_dataset(expected_file)
    assert_close(dataset, expected, check_attrs=False)
