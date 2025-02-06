import xarray as xr

# import matplotlib.dates as mdates
# import matplotlib.pyplot as plt
from tsdat import TransformationPipeline


# Implement your pipeline and update its docstring.
class VapSpotterApi(TransformationPipeline):
    def hook_customize_input_datasets(self, input_datasets):

        return input_datasets

    def hook_customize_dataset(self, dataset: xr.Dataset) -> xr.Dataset:
        # (Optional) Use this hook to modify the dataset before qc is applied
        dataset.attrs.pop("description")

        return dataset

    def hook_finalize_dataset(self, dataset: xr.Dataset) -> xr.Dataset:
        # (Optional) Use this hook to modify the dataset after qc is applied
        # but before it gets saved to the storage area
        return dataset

    def hook_plot_dataset(self, dataset: xr.Dataset):
        # (Optional, recommended) Create plots.
        # location = self.dataset_config.attrs.location_id
        # datastream: str = self.dataset_config.attrs.datastream

        # date, time = get_start_date_and_time_str(dataset)

        # with plt.style.context("shared/styling.mplstyle"):
        #     fig, ax = plt.subplots()
        #     dataset["example_var"].plot(ax=ax, x="time")  # type: ignore
        #     fig.suptitle(f"Example Variable at {location} on {date} {time}")
        #     plot_filepath = self.get_ancillary_filepath(title="example_plot")
        #     fig.savefig(plot_filepath)
        #     plt.close(fig)
        pass
