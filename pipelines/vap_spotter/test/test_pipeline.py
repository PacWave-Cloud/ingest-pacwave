from pathlib import Path
import pytest
import xarray as xr
from tsdat import assert_close, PipelineConfig, TransformationPipeline


# The transformation pipeline will likely depend on the output of an ingestion pipeline
# in order to declare this dependency so the tests can run in the correct order (e.g.,
# for github actions CI/CD), update the line below to point to the correct folder and
# test name
@pytest.mark.dependency(depends=["../../spotter/test/test_pipeline.py"])
def test_vap_spotter_pipeline():
    # The transformation pipeline will likely depend on the output of an ingestion
    # pipeline. To account for this we first run the ingest to generate input data for
    # the vap, and then run the vap test. Please update the line below to point to the
    #  correct folder / test name
    from pipelines.spotter.test.test_pipeline import test_pacwave_pipeline_api_pacwave

    test_pacwave_pipeline_api_pacwave()

    config_path = Path("pipelines/vap_spotter/config/pipeline_30903C_pws.yaml")
    config = PipelineConfig.from_yaml(config_path)
    # Manually set to storage so tests pass
    config.storage.parameters["storage_root"] = "storage"
    pipeline: TransformationPipeline = config.instantiate_pipeline()  # type: ignore

    # Transformation pipelines require an input of [date.time, date.time] formatted as
    # YYYYMMDD.hhmmss. The start date is inclusive, the end date is exclusive.
    run_dates = ["20250101.000000", "20250201.000000"]
    dataset = pipeline.run(run_dates)

    # You will need to create this file after running the data through the pipeline
    # OR: Delete this and perform sanity checks on the input data instead of comparing
    # with an expected output file
    expected_file = "pipelines/vap_spotter/test/data/expected/pws.spotter-30903C.c2.20250111.003000.nc"
    expected: xr.Dataset = xr.open_dataset(expected_file)  # type: ignore
    assert_close(dataset, expected, check_attrs=False)
