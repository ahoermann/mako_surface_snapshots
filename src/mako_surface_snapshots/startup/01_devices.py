from mako_surface_snapshots.devices import Vimba

vimba = Vimba("13VMB1:", name="vimba")

# do not connect to the sample stage during tests
# sample_stage_gi = SampleStageGI("newport1:", name = "sample_stage_gi")
