from __future__ import annotations
from typing import Iterator

from bluesky import plan_stubs as bps


def vimba_capture(vimba, exposure_time: float = 1) -> Iterator:
    yield from bps.stage(vimba)
    try:
        yield from bps.trigger_and_read([vimba], name="mouse_vimba_measure")
    finally:
        yield from bps.unstage(vimba)
