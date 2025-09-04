import xarray as xr
from pathlib import Path
from tsdat import PipelineConfig, assert_close


def test_uplookingADCP_pipeline1():
    config_path = Path("pipelines/up_looking_adcp/config/pipeline.yaml")
    config = PipelineConfig.from_yaml(config_path)
    # Manually set to storage so tests pass
    config.storage.parameters["storage_root"] = "storage"
    pipeline = config.instantiate_pipeline()

    test_file = (
        "pipelines/up_looking_adcp/test/data/input/S104922A003_PWS_SITE_01.ad2cp"
    )
    expected_file = "pipelines/up_looking_adcp/test/data/expected/pws.bottom_adcp-001.a1.20240424.200000.nc"

    dataset = pipeline.run([test_file])
    expected: xr.Dataset = xr.open_dataset(expected_file)  # type: ignore
    assert_close(dataset, expected, check_attrs=False)


def test_uplookingADCP_pipeline2():
    config_path = Path("pipelines/up_looking_adcp/config/pipeline.yaml")
    config = PipelineConfig.from_yaml(config_path)
    # Manually set to storage so tests pass
    config.storage.parameters["storage_root"] = "storage"
    pipeline = config.instantiate_pipeline()

    test_file = (
        "pipelines/up_looking_adcp/test/data/input/S104922A004_PWS_SITE_02.ad2cp"
    )
    expected_file = "pipelines/up_looking_adcp/test/data/expected/pws.bottom_adcp-001.a1.20241022.192936.nc"

    dataset = pipeline.run([test_file])
    expected: xr.Dataset = xr.open_dataset(expected_file)  # type: ignore
    assert_close(dataset, expected, check_attrs=False)
