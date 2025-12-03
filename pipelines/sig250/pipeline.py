import numpy as np
import xarray as xr
from pathlib import Path
from mhkit.tidal import graphics
from tsdat import IngestPipeline
import matplotlib as mpl
import matplotlib.pyplot as plt


class UpLookingSig250(IngestPipeline):
    def hook_customize_dataset(self, dataset: xr.Dataset) -> xr.Dataset:
        # (Optional) Use this hook to modify the dataset before qc is applied

        filename = Path(dataset.inputs).stem
        qualifier = filename.split("_")[-1]
        dataset.attrs["qualifier"] = "0" + qualifier
        dataset.attrs["datastream"] = dataset.attrs["datastream"].replace(
            "001", "0" + qualifier
        )

        return dataset

    def hook_finalize_dataset(self, dataset: xr.Dataset) -> xr.Dataset:
        # (Optional) Use this hook to modify the dataset after qc is applied
        # but before it gets saved to the storage area

        return dataset

    def hook_plot_dataset(self, ds: xr.Dataset):
        max_depth = 75  # m
        adcp_bin = 60  # m
        umax = 0.8  # m/s

        with plt.style.context("shared/styling.mplstyle"):
            # Water velocity
            fig, ax = plt.subplots(3, figsize=(10, 7), constrained_layout=True)
            h1 = ax[0].pcolor(
                ds["time_avg"].values,
                ds["range_avg"].values,
                ds["vel_avg"][0],
                cmap="coolwarm_r",
                vmin=-umax,
                vmax=umax,
            )
            label = "Velocity " + str(ds["vel_avg"].dir[0].values) + " [m/s]"
            fig.colorbar(h1, ax=ax[0], label=label, fraction=0.05, pad=0.02)
            ax[0].set(xlabel="Time", ylabel="Depth [m]", ylim=(0, max_depth))

            h2 = ax[1].pcolor(
                ds["time_avg"].values,
                ds["range_avg"].values,
                ds["vel_avg"][1],
                cmap="coolwarm_r",
                vmin=-umax,
                vmax=umax,
            )
            label = "Velocity " + str(ds["vel_avg"].dir[1].values) + " [m/s]"
            fig.colorbar(h2, ax=ax[1], label=label, fraction=0.05, pad=0.02)
            ax[1].set(xlabel="Time", ylabel="Depth [m]", ylim=(0, max_depth))

            h3 = ax[2].pcolor(
                ds["time_avg"].values,
                ds["range_avg"].values,
                ds["vel_avg"][2],
                cmap="coolwarm_r",
                vmin=-0.1,
                vmax=0.1,
            )
            label = "Velocity " + str(ds["vel_avg"].dir[2].values) + " [m/s]"
            fig.colorbar(h3, ax=ax[2], label=label, fraction=0.05, pad=0.02)
            ax[2].set(xlabel="Time", ylabel="Depth [m]", ylim=(0, max_depth))

            plot_file = self.get_ancillary_filepath(title="current")
            fig.savefig(plot_file)
            plt.close(fig)

            # # Amplitude
            # fig, ax = plt.subplots(
            #     nrows=ds.n_beams, ncols=1, figsize=(14, 8), constrained_layout=True
            # )

            # for beam in range(ds.n_beams):
            #     amp = ax[beam].pcolormesh(
            #         ds["time_avg"].values,
            #         ds["range_avg"],
            #         ds["amp_avg"][beam],
            #         shading="nearest",
            #     )
            #     ax[beam].set_title("Beam " + str(beam + 1))
            #     ax[beam].set(xlabel="Time (UTC)", ylabel=r"Range [m]", ylim=(0, y_max))
            #     add_colorbar(ax[beam], amp, "Amplitude [dB]")

            # plot_file = self.get_ancillary_filepath(title="amplitude")
            # fig.savefig(plot_file)
            # plt.close(fig)

            # # Correlation
            # fig, ax = plt.subplots(
            #     nrows=ds.n_beams, ncols=1, figsize=(14, 8), constrained_layout=True
            # )

            # for beam in range(ds.n_beams):
            #     corr = ax[beam].pcolormesh(
            #         ds["time_avg"].values,
            #         ds["range_avg"],
            #         ds["corr_avg"][beam],
            #         cmap="copper",
            #         shading="nearest",
            #     )
            #     ax[beam].set_title("Beam " + str(beam + 1))
            #     ax[beam].set(xlabel="Time (UTC)", ylabel=r"Range [m]", ylim=(0, y_max))
            #     add_colorbar(ax[beam], corr, "Correlation [%]")

            # plot_file = self.get_ancillary_filepath(title="correlation")
            # fig.savefig(plot_file)
            # plt.close(fig)

            # Plot water speed and direction
            fig, ax = plt.subplots(
                nrows=2, ncols=1, figsize=(10, 5), constrained_layout=True
            )
            speed = ax[0].pcolormesh(
                ds["time_avg"].values,
                ds["range_avg"],
                ds["speed"],
                cmap="Blues",
                shading="nearest",
                vmin=0,
                vmax=umax,
            )
            label = "Water Speed [m/s]"
            fig.colorbar(speed, ax=ax[0], label=label, fraction=0.05, pad=0.02)
            ax[0].set(ylabel="Altitude [m]", ylim=(0, max_depth))

            dirc = ax[1].pcolormesh(
                ds["time_avg"].values,
                ds["range_avg"],
                ds["direction"],
                cmap="twilight",
                shading="nearest",
                vmin=0,
                vmax=360,
            )
            label = "Water Direction [deg CW from N]"
            fig.colorbar(dirc, ax=ax[1], label=label, fraction=0.05, pad=0.02)
            ax[1].set(xlabel="Time", ylabel="Altitude [m]", ylim=(0, max_depth))

            plot_file = self.get_ancillary_filepath(title="speed_avg")
            fig.savefig(plot_file)
            plt.close(fig)

            # Plot IMU
            fig, ax = plt.subplots(3, figsize=(10, 7), constrained_layout=True)
            ax[0].plot(ds["time_avg"].values, ds["heading_avg"])
            ax[0].set(xlabel="Time", ylabel="Heading [deg]")

            ax[1].plot(ds["time_avg"].values, ds["pitch_avg"])
            ax[1].set(xlabel="Time", ylabel="Pitch [deg]")

            ax[2].plot(ds["time_avg"].values, ds["roll_avg"])
            ax[2].set(xlabel="Time", ylabel="Roll [deg]")

            plot_file = self.get_ancillary_filepath(title="environment")
            fig.savefig(plot_file)
            plt.close(fig)

            # Plot CTD
            if hasattr(ds, "altitude"):
                fig, ax = plt.subplots(4, figsize=(10, 7), constrained_layout=True)
            else:
                fig, ax = plt.subplots(3, figsize=(10, 7), constrained_layout=True)

            ax[0].plot(ds["time_avg"].values, ds["depth_avg"])
            ax[0].set(xlabel="Time", ylabel="Instrument Depth [m]")

            ax[1].plot(ds["time_avg"].values, ds["temperature_avg"])
            ax[1].set(xlabel="Time", ylabel="Water Temperature [C]")

            ax[2].plot(ds["time_avg"].values, ds["speed_of_sound_avg"])
            ax[2].set(xlabel="Time", ylabel="Speed of Sound [m/s]")

            if hasattr(ds, "altitude"):
                ax[3].plot(ds["time"].values, ds["altitude"])
                ax[3].set(xlabel="Time", ylabel="Instrument Altitude [m]")

            plot_file = self.get_ancillary_filepath(title="environment")
            fig.savefig(plot_file)
            plt.close(fig)

            # Plot joint probability distributions
            def plot(U, D, ax):
                ax = graphics.plot_joint_probability_distribution(
                    directions=D.to_series(),
                    velocities=U.to_series(),
                    ax=ax,
                    width_dir=5,
                    width_vel=0.1,
                )
                ax.set_rmax(umax)
                ax.set_rticks(np.arange(0.1, umax + 0.1, 0.2))
                ax.set_rlabel_position(-70)
                ax.set_yticklabels(
                    [f"{np.round(y, 1)} m/s" for y in np.arange(0.1, umax + 0.1, 0.2)]
                )
                ax.tick_params("y", labelrotation=60)

                sx = ax.get_children()[0]  # get scatter handle
                sx.set_cmap(cmap)
                sx.set_norm(norm)

                return ax

            fig, ax = plt.subplots(
                1,
                1,
                figsize=(5, 4),
                subplot_kw={"projection": "polar"},
                constrained_layout=True,
            )

            # Set colors after plotting
            cmap = plt.cm.viridis
            vmax = 12
            bounds = np.linspace(0, vmax, 256)
            norm = mpl.colors.BoundaryNorm(bounds, cmap.N)
            plot(
                ds["speed"].sel({"range_avg": adcp_bin}, method="nearest"),
                ds["direction"].sel({"range_avg": adcp_bin}, method="nearest"),
                ax,
            )
            plot_file = self.get_ancillary_filepath(title="rose")
            fig.savefig(plot_file)
            plt.close(fig)
