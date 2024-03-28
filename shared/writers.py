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

    storage_model = StorageConfig(classname="tsdat.io.storage.FileSystem")
    storage = recursive_instantiate(storage_model)
    storage.handler.writer = CSVWriter()
    storage.save_data(dataset)
