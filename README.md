sc6_camera
==========

webcam fetching and timelapse generating / publishing tool

totally written for my own needs, but perhaps useful to others

Bins:
cam_collect_images - persistant script harvesting images, launches from upstart
build_time_lapse.pl
hourly.sh
push2youtube.py

Tools:
blueist.pl - tests bluecode algorithms for a set of images
do_overlays.pl - test for overlays
gap_check.pl - gives feedback on regularity of images
how_blue.pl - blue code testing
image.pl - fetches one image and processes it
mv_files.pl - scipt for moving some files around
sun.pl - script for testing sun calculations
wx.pl - script for testing some wx functions

Docs:
rrd_data_sets - my rrd data set definitions
wx_cmds - my commands for extracting wx data

Init:
Here are configs for either upstart or systemd
install/updtart - upstart config files
install/systemd - systemd config files
