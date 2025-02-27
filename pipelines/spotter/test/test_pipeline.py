import xarray as xr
from pathlib import Path
from tsdat import PipelineConfig, assert_close


def test_pacwave_pipeline_csv():
    config_path = Path("pipelines/spotter/config/pipeline_30897C.yaml")
    config = PipelineConfig.from_yaml(config_path)
    # Manually set to storage so tests pass
    config.storage.parameters["storage_root"] = "storage"
    pipeline = config.instantiate_pipeline()
    test_file = (
        "pipelines/spotter/test/input/SPOT-30897C_2024-02-29_2024-03-02_download.csv"
    )
    expected_file = (
        "pipelines/spotter/test/expected/pwn.spotter-30897C.c1.20240229.170000.nc"
    )

    dataset = pipeline.run([test_file])
    expected: xr.Dataset = xr.open_dataset(expected_file)
    assert_close(dataset, expected, check_attrs=False)


def test_pacwave_pipeline_api_example():
    config_path = Path("pipelines/spotter/config/pipeline_json.yaml")
    config = PipelineConfig.from_yaml(config_path)
    # Manually set to storage so tests pass
    config.storage.parameters["storage_root"] = "storage"
    pipeline = config.instantiate_pipeline()

    test_file = "pipelines/spotter/test/input/spot-1945.json"
    expected_file = (
        "pipelines/spotter/test/expected/pws.spotter-1945.c1.20210901.002528.nc"
    )

    dataset = pipeline.run([test_file])
    expected: xr.Dataset = xr.open_dataset(expected_file)
    assert_close(dataset, expected, check_attrs=False)


def test_pacwave_pipeline_api_pacwave():
    config_path = Path("pipelines/spotter/config/pipeline_json.yaml")
    config = PipelineConfig.from_yaml(config_path)
    # Manually set to storage so tests pass
    config.storage.parameters["storage_root"] = "storage"
    pipeline = config.instantiate_pipeline()

    test_file = "pipelines/spotter/test/input/spot-30903c.20250111T000000Z.json"
    expected_file = (
        "pipelines/spotter/test/expected/pws.spotter-30903C.c1.20250111.003000.nc"
    )

    dataset = pipeline.run([test_file])
    expected: xr.Dataset = xr.open_dataset(expected_file)
    assert_close(dataset, expected, check_attrs=False)


def test_pacwave_pipeline_api_no_temp():
    config_path = Path("pipelines/spotter/config/pipeline_json.yaml")
    config = PipelineConfig.from_yaml(config_path)
    # Manually set to storage so tests pass
    config.storage.parameters["storage_root"] = "storage"
    pipeline = config.instantiate_pipeline()

    test_file = "pipelines/spotter/test/input/spot-30897c.00.20250127T000000Z.json"
    expected_file = (
        "pipelines/spotter/test/expected/pwn.spotter-30897C.c1.20250127.223500.nc"
    )

    dataset = pipeline.run([test_file])
    expected: xr.Dataset = xr.open_dataset(expected_file)
    assert_close(dataset, expected, check_attrs=False)
