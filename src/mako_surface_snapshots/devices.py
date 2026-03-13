from ophyd import Component as Cpt
from ophyd.areadetector import ADComponent, DetectorBase
from ophyd.areadetector.cam import CamBase
from ophyd.areadetector.plugins import ImagePlugin, StatsPlugin
from ophyd.areadetector.trigger_mixins import SingleTrigger

# https://blueskyproject.io/ophyd/user/tutorials/device.html
from ophyd import (
    Device,
    EpicsMotor,
)


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


class Vimba(SingleTrigger, DetectorBase):
    cam = ADComponent(CamBase, "cam1:")
    image = ADComponent(ImagePlugin, "image1:")
    stats1 = ADComponent(StatsPlugin, "Stats1:")
