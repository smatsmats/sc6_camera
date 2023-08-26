sc6_camera
==========

webcam fetching and timelapse generating / publishing tool

totally written for my own needs, but perhaps useful to others

Bins:
build_and_push.pl - wrapper for build and push cron job
cam_collect_images - persistant script harvesting images, launches from upstart
build_time_lapse.pl
push2youtube.py
blueist.pl - tests bluecode algorithms for a set of images
do_overlays.pl - test for overlays
gap_check.pl - gives feedback on regularity of images
how_blue.pl - blue code testing
image.pl - fetches one image and processes it
mv_files.pl - script for moving some files around
sun.pl - script for testing sun calculations
wx.pl - script for testing some wx functions
template_test.py - useful for testing how your title and description will be built before pushing the video to youtube

Docs:
rrd_data_sets - my rrd data set definitions
wx_cmds - my commands for extracting wx data

Init:
Here are configs for either upstart or systemd
install/upstart - upstart config files
install/systemd - systemd config files

Oauth Tokens for YouTube:

Once you've created the credentials entry in gogole developers console and copied the client id and client secret run either 
of the youtube scripts and walk thru the permissions flow.  You'll need a browser with javascript.  If you're running headless 
you may need to fire-up an X11 server somewhere to get a full-enough browser

Some things that will be needed:

sudo apt-get install mencoder
sudo apt-get install ffmpeg

pip install install google-api-python-client
pip install --upgrade google-cloud-storage
pip install astral
