#!/usr/bin/perl

#time /usr/local/cam/bin/build_time_lapse.pl 
my $ret = `trickle -s -u 200 /usr/local/cam/bin/build_time_lapse.pl $@`;
if ( $? != 0 ) {
    print $ret;
}
