#!/bin/sh

#time /usr/local/cam/bin/build_time_lapse.pl 
time trickle -s -u 200 /usr/local/cam/bin/build_time_lapse.pl $@
