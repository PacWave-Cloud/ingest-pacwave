import logging
from pathlib import Path
from tsdat.config.storage import StorageConfig
from tsdat.config.utils import recursive_instantiate
from tsdat.io.writers import CSVWriter


logger = logging.getLogger(__name__)


def write_csv(dataset):
    """----------------------------------------------------------------------------
    Saves pipeline data in a CSV format using tsdat's built-in CSV writer.

    Args:
        dataset (xarray.dataset): Pipeline dataset
    ----------------------------------------------------------------------------"""

    storage_model = StorageConfig.from_yaml(Path("shared/storage.yaml"))
    try:
        storage = recursive_instantiate(storage_model)
        storage.handler.writer = CSVWriter()
        storage.save_data(dataset)
    except:  # for tests
        storage_model.parameters["storage_root"] = "storage/root"
        storage = recursive_instantiate(storage_model)
        storage.handler.writer = CSVWriter()
        storage.save_data(dataset)
