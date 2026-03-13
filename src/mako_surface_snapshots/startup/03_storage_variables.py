DATABROKER_ROOT_PATH = "/tmp/"

# note: AD path MUST, must, MUST have trailing "/"!!!
#  ...and... start with the same path defined in root (above)

# path as seen by detector IOC
WRITE_HDF5_FILE_PATH = "/tmp/simdet/%Y/%m/%d/"
#!!! NOTE !!! This filesystem is on the IOC

# path as seen by bluesky data acquistion
READ_HDF5_FILE_PATH = "/tmp/docker_ioc/iocadsky/tmp/simdet/%Y/%m/%d/"
