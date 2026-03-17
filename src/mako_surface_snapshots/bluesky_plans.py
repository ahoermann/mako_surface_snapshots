from __future__ import annotations
from typing import Iterator
from pathlib import Path

from bluesky import plan_stubs as bps
from bayes_opt import BayesianOptimization, SequentialDomainReductionTransformer
from bayes_opt.acquisition import ExpectedImprovement

from mako_surface_snapshots.devices import ad_configure_exposure


def vimba_capture(
    vimba, exposure_time: float = 1, output_path: Path = Path("/tmp/current/")
) -> Iterator:
    yield from ad_configure_exposure(
        vimba, exposure_time=exposure_time, output_path=output_path
    )
    yield from bps.stage(vimba)
    try:
        yield from bps.trigger_and_read([vimba], name="mouse_vimba_measure")
    finally:
        yield from bps.unstage(vimba)


def vimba_read(
    vimba, exposure_time: float = 1, output_path: Path = Path("/tmp/current/")
) -> Iterator:
    yield from bps.open_run()
    yield from vimba_capture(
        vimba, exposure_time=exposure_time, output_path=output_path
    )
    array_size = vimba.image.array_size.get()
    shape = (array_size.height, array_size.width)
    # img = vimba.image.array_data.get().reshape(shape)
    # plt.imshow(img)
    # plt.savefig(output_path / "latest.png")
    # plt.close()
    yield from bps.close_run()


def vimba_optimise_gain(vimba, exposure_time: float = 0.5) -> Iterator:
    yield from ad_configure_exposure(
        vimba, exposure_time=exposure_time, output_path=output_path
    )

    def black_box_function(vimba=vimba, exposure_time=exposure_time, **kwargs):
        for key, value in kwargs.items():
            yield from bps.mv(vimba.cam.Gain, value)
        yield from bps.open_run()
        yield from vimba_capture(
            vimba, exposure_time=exposure_time, output_path=output_path
        )
        yield from bps.close_run()
        array_size = vimba.image.array_size.get()
        shape = (array_size.height, array_size.width)
        img = vimba.image.array_data.get().reshape(shape)
        brightness = 100 * np.mean(img) / 255
        return 1e-6 + 1 / (abs(brightness - 30))

    def optimize(init_points=10, n_iter=10):
        acquisition_function = ExpectedImprovement(xi=1e-4)
        optimizer = BayesianOptimization(
            f=black_box_function,
            pbounds={"Gain": (0, 40)},
            random_state=1,
            bounds_transformer=SequentialDomainReductionTransformer(),
            acquisition_function=acquisition_function,
        )
        optimizer.maximize(
            init_points=init_points,
            n_iter=n_iter,
        )
        return 0

    yield from optimize()
