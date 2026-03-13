from pathlib import Path

from ophyd import Component as Cpt
from ophyd.areadetector import ADComponent, DetectorBase
from ophyd.areadetector.cam import CamBase
from ophyd.areadetector.plugins import ImagePlugin, StatsPlugin
from ophyd.areadetector import HDF5Plugin
from ophyd.areadetector import EpicsSignalWithRBV
from ophyd.areadetector.filestore_mixins import FileStoreHDF5IterativeWrite
from ophyd.areadetector.trigger_mixins import SingleTrigger

# https://blueskyproject.io/ophyd/user/tutorials/device.html
from ophyd import (
    Device,
    EpicsMotor,
)

import bluesky.plan_stubs as bps


class SampleStageGI(Device):
    """
    This device connects to the sample stage. Names are constructed by concatenation
    """

    def __init__(self, *args, **kwargs):  # slit_number:int|None = None
        super().__init__(*args, **kwargs)

    y = Cpt(EpicsMotor, "ysam")
    # z = Cpt(EpicsMotor, "zheavy")  # different address for now
    pitch = Cpt(EpicsMotor, "pitchgi")
    roll = Cpt(EpicsMotor, "rollgi")
    yaw = Cpt(EpicsMotor, "yaw")


# from https://bcda-aps.github.io/bluesky_training/tutor/_lesson6.html
class MyHDF5Plugin(HDF5Plugin, FileStoreHDF5IterativeWrite):
    create_directory_depth = Cpt(EpicsSignalWithRBV, suffix="CreateDirectory")
    array_callbacks = Cpt(EpicsSignalWithRBV, suffix="ArrayCallbacks")

    pool_max_buffers = None

    def get_frames_per_point(self):
        return self.num_capture.get()

    def stage(self):
        super().stage()
        res_kwargs = {"frame_per_point": self.get_frames_per_point()}
        # res_kwargs = {'frame_per_point': self.num_capture.get()}
        self._generate_resource(res_kwargs)


class Vimba(SingleTrigger, DetectorBase):
    cam = ADComponent(CamBase, "cam1:")
    image = ADComponent(ImagePlugin, "image1:")
    stats1 = ADComponent(StatsPlugin, "Stats1:")
    output_path = Path("/tmp/images/")
    hdf1 = ADComponent(
        MyHDF5Plugin,
        suffix="HDF1:",
        root=Path(".").absolute().as_posix(),
        write_path_template=f"{Path('.').absolute().as_posix()}/%Y/%m/%d/",
        read_path_template=f"{Path('.').absolute().as_posix()}/%Y/%m/%d/",
    )


def ad_configure_exposure(
    det, exposure_time: int = 1, output_path: Path | str = "/tmp/current/"
):
    def split_exposure_time_to_frames_and_time(exposure_time):
        # Eiger can only acquire frames of up to 10s, so we need to split the exposure time into multiple frames if it's longer than that.
        if exposure_time <= 0:
            exposure_time = 1  # dumbasses.
        if exposure_time <= 10:
            return 1, exposure_time
        else:
            n_frames = int(np.ceil(exposure_time / 10))
            frame_time = exposure_time / n_frames
            return n_frames, frame_time

    n_frames, frame_time = split_exposure_time_to_frames_and_time(exposure_time)
    out_path = Path(output_path)  # this is a directory
    if not out_path.exists():
        # create
        out_path.mkdir(parents=True, exist_ok=True)
    out_path = out_path.absolute().as_posix()  # convert to string for EPICS

    yield from bps.mv(det.cam.num_images, int(n_frames))
    yield from bps.mv(det.cam.acquire_time, frame_time)
    yield from bps.mv(det.cam.acquire_period, frame_time)
    yield from bps.mv(det.hdf1.num_capture, 1)
    # not sure what the correct way to configure paths is here
    # yield from bps.mv(det.hdf1.write_path_template, output_path / "%Y/%m/%d/")

    det.output_path = Path(output_path)
