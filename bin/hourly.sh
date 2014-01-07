#!/bin/sh

#time /usr/local/cam/bin/build_time_lapse.pl 
time trickle -sv -u 200 /usr/local/cam/bin/build_time_lapse.pl $@
