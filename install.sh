#!/bin/sh

#sudo cp etc/init/cam_collect_images.conf /etc/init
#sudo cp etc/default/cam_collect_images /etc/default

[ -d /usr/local/lib/site_perl/SC6/Cam/ ] || sudo mkdir -p /usr/local/lib/site_perl/SC6/Cam

./install_libs.sh

[ -d /usr/local/cam/conf/ ] || sudo mkdir -p /usr/local/cam/conf/
sudo cp -p conf/config.yml /usr/local/cam/conf
sudo cp -p conf/push2youtube_config.yml /usr/local/cam/conf
sudo cp -p conf/logging.yml /usr/local/cam/conf

[ -d /usr/local/cam/bin/ ] || sudo mkdir -p /usr/local/cam/bin/
sudo cp -p bin/cam_collect_images /usr/local/cam/bin
sudo cp -p bin/ls_today_vids.py /usr/local/cam/bin
sudo cp -p bin/cam_status /usr/local/cam/bin
sudo cp -p bin/sun.pl /usr/local/cam/bin
sudo cp -p bin/bucket_shiz.py /usr/local/cam/bin

[ -d /usr/local/cam/sekrits/ ] || sudo mkdir -p /usr/local/cam/sekrits/

cp www/index.cgi /home/willey/sc6_camera_www

crontab -l > /tmp/old_cron
cat cron/crontab /tmp/old_cron | crontab -

