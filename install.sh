#!/bin/sh

sudo cp etc/init/cam_collect_images.conf /etc/init
sudo cp etc/default/cam_collect_images /etc/default

[ -d /usr/local/lib/site_perl/SC6/Cam/ ] || sudo mkdir -p /usr/local/lib/site_perl/SC6/Cam

sudo cp lib/site_perl/SC6/Cam/BlueCode.pm  /usr/local/lib/site_perl/SC6/Cam
sudo cp lib/site_perl/SC6/Cam/BlueCodeState.pm  /usr/local/lib/site_perl/SC6/Cam
sudo cp lib/site_perl/SC6/Cam/Config.pm  /usr/local/lib/site_perl/SC6/Cam
sudo cp lib/site_perl/SC6/Cam/General.pm  /usr/local/lib/site_perl/SC6/Cam
sudo cp lib/site_perl/SC6/Cam/GStore.pm  /usr/local/lib/site_perl/SC6/Cam
sudo cp lib/site_perl/SC6/Cam/Image.pm  /usr/local/lib/site_perl/SC6/Cam
sudo cp lib/site_perl/SC6/Cam/Overlay.pm  /usr/local/lib/site_perl/SC6/Cam
sudo cp lib/site_perl/SC6/Cam/Sun.pm  /usr/local/lib/site_perl/SC6/Cam
sudo cp lib/site_perl/SC6/Cam/WX.pm  /usr/local/lib/site_perl/SC6/Cam

crontab -l > /tmp/old_cron
cat cron/crontab /tmp/old_cron | crontab -

