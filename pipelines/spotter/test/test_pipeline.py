import xarray as xr
from pathlib import Path
from tsdat import PipelineConfig, assert_close
import os


def test_pacwave_pipeline():
    spotter = "30897C"
    test_file = f"pipelines/pacwave/test/data/input/spotter_{spotter}/pacwave.spot.{spotter}.20231201.csv"

    if spotter != "0401":
        config_path = Path(f"pipelines/pacwave/config/pipeline_spotter_{spotter}.yaml")
    else:
        config_path = Path("pipelines/pacwave/config/pipeline.yaml")

    config = PipelineConfig.from_yaml(config_path)
    pipeline = config.instantiate_pipeline()

    dataset = pipeline.run([test_file])
