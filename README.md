sc6_camera
==========

webcam fetching and timelapse generating / publishing tool

totally written for my own needs, but perhaps useful to others

In the glacially slow process of moving from Perl to Python. Currently a mix of both.  

Bins (needs updating):
<ul>
<li>build_and_push.py - builds hourly videos and pushes somewhere
<li>cam_collect_images - persistant script harvesting images
<li>build_time_lapse.pl
<li>push2youtube.py
<li>blueist.pl - tests bluecode algorithms for a set of images
<li>do_overlays.pl - test for overlays
<li>gap_check.pl - gives feedback on regularity of images
<li>how_blue.pl - blue code testing
<li>image.pl - fetches one image and processes it
<li>mv_files.pl - script for moving some files around
<li>sun.pl - script for testing sun calculations
<li>wx.pl - script for testing some wx functions
<li>template_test.py - useful for testing how your title and description will be built before pushing the video to youtube
</ul>

Docs:<br>
rrd_data_sets - my rrd data set definitions<br>
wx_cmds - my commands for extracting wx data

Init:<br>
Here are configs for either upstart or systemd<br>
install/upstart - upstart config files<br>
install/systemd - systemd config files<br>

Oauth Tokens for YouTube:

Once you've created the credentials entry in gogole developers console and copied the client id and client secret run either 
of the youtube scripts and walk thru the permissions flow.  You'll need a browser with javascript.  If you're running headless 
you may need to fire-up an X11 server somewhere to get a full-enough browser

Some things that will be needed:

<code>sudo apt-get install mencoder
sudo apt-get install ffmpeg
pip install install google-api-python-client
pip install --upgrade google-cloud-storage
pip install astral
</code>

If you want to do AWS storage
<code>
pip install boto3
</code>
