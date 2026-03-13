from collections import OrderedDict
import time

from mako_surface_snapshots.devices import Vimba

DATABROKER_ROOT_PATH = "/tmp/"

# note: AD path MUST, must, MUST have trailing "/"!!!
#  ...and... start with the same path defined in root (above)

# path as seen by detector IOC
WRITE_HDF5_FILE_PATH = "/tmp/simdet/%Y/%m/%d/"
#!!! NOTE !!! This filesystem is on the IOC

# path as seen by bluesky data acquistion
READ_HDF5_FILE_PATH = "/tmp/docker_ioc/iocadsky/tmp/simdet/%Y/%m/%d/"


vimba = Vimba("13VMB1:", name="vimba")

# can't get warmup to work: TriggerMode 'Internal' not in allowed values
vimba.read_attrs.append("hdf1")
enabled = vimba.hdf1.enable.get()
# vimba.hdf1.warmup()


def warmup_hdf5(hdf5plugin):
    sigs = OrderedDict(
        [
            (hdf5plugin.parent.cam.array_callbacks, 1),
            (hdf5plugin.parent.cam.image_mode, "Single"),
            (hdf5plugin.parent.cam.trigger_mode, "On"),
            # just in case tha acquisition time is set very long...
            (hdf5plugin.parent.cam.acquire_time, 1),
            (hdf5plugin.parent.cam.acquire_period, 1),
            (hdf5plugin.parent.cam.acquire, 1),
        ]
    )

    original_vals = {sig: sig.get() for sig in sigs}

    for sig, val in sigs.items():
        time.sleep(0.1)  # abundance of caution
        sig.set(val).wait()

    time.sleep(2)  # wait for acquisition

    for sig, val in reversed(list(original_vals.items())):
        time.sleep(0.1)
        sig.set(val).wait()


warmup_hdf5(vimba.hdf1)
vimba.hdf1.enable.put(enabled)


# do not connect to the sample stage during tests
# sample_stage_gi = SampleStageGI("newport1:", name = "sample_stage_gi")
