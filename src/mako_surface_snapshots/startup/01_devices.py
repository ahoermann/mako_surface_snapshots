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

vimba.read_attrs.append("hdf1")
enabled = vimba.hdf1.enable.get()
vimba.hdf1.warmup()
vimba.hdf1.enable.put(enabled)


# do not connect to the sample stage during tests
# sample_stage_gi = SampleStageGI("newport1:", name = "sample_stage_gi")
