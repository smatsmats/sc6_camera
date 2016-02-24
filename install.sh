#!/bin/sh

sudo cp etc/init/cam_collect_images.conf /etc/init
sudo cp etc/default/cam_collect_images /etc/default

[ -d /usr/local/lib/site_perl/SC6/Cam/ ] || sudo mkdir -p /usr/local/lib/site_perl/SC6/Cam

./install_libs.sh

cp www/index.cgi /home/willey/sc6_camera_www

crontab -l > /tmp/old_cron
cat cron/crontab /tmp/old_cron | crontab -

