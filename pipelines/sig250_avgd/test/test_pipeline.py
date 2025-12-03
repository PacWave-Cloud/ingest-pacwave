import xarray as xr
from pathlib import Path
from tsdat import PipelineConfig, assert_close


def test_UpLookingSig250_pipeline_avg1():
    config_path = Path("pipelines/sig250_avgd/config/pipeline_pws.yaml")
    config = PipelineConfig.from_yaml(config_path)
    # Manually set to storage so tests pass
    config.storage.parameters["storage_root"] = "storage"
    pipeline = config.instantiate_pipeline()

    test_file = (
        "pipelines/sig250_avgd/test/data/input/S104922A003_PWS_SITE_01_avgd.ad2cp"
    )
    expected_file = "pipelines/sig250_avgd/test/data/expected/pws.sig250_avgd-001.a1.20240424.200059.nc"

    dataset = pipeline.run([test_file])
    expected: xr.Dataset = xr.open_dataset(expected_file)  # type: ignore
    assert_close(dataset, expected, check_attrs=False)


def test_UpLookingSig250_pipeline_avg2():
    config_path = Path("pipelines/sig250_avgd/config/pipeline_pws.yaml")
    config = PipelineConfig.from_yaml(config_path)
    # Manually set to storage so tests pass
    config.storage.parameters["storage_root"] = "storage"
    pipeline = config.instantiate_pipeline()

    test_file = (
        "pipelines/sig250_avgd/test/data/input/S104922A004_PWS_SITE_02_avgd.ad2cp"
    )
    expected_file = "pipelines/sig250_avgd/test/data/expected/pws.sig250_avgd-002.a1.20241022.193035.nc"

    dataset = pipeline.run([test_file])
    expected: xr.Dataset = xr.open_dataset(expected_file)  # type: ignore
    assert_close(dataset, expected, check_attrs=False)
