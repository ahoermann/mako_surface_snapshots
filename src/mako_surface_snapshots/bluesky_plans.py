from __future__ import annotations
from typing import Iterator
from pathlib import Path

from bluesky import plan_stubs as bps

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
