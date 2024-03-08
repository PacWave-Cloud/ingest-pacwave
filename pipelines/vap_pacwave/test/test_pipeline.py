from pathlib import Path

import pytest
import xarray as xr
from tsdat import assert_close, PipelineConfig, TransformationPipeline


def test_vap_pacwave_pipeline():
    spotter = "30904c"

    if spotter != "0401":
        config_path = Path(
            f"pipelines/vap_pacwave/config/pipeline_spotter_{spotter}.yaml"
        )
    else:
        config_path = Path("pipelines/vap_pacwave/config/pipeline.yaml")

    config = PipelineConfig.from_yaml(config_path)
    pipeline: TransformationPipeline = config.instantiate_pipeline()  # type: ignore

    run_dates = ["20231201.000000", "20231231.000000"]
    dataset = pipeline.run(run_dates)
