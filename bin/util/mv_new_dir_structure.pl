#!/usr/bin/perl

use File::Path 'make_path';

my $d = "/usr/local/cam/data/cam_images/";

opendir(my $dh, $d) || die;

while(readdir $dh) {
    next if ( $_ eq "." );
    next if ( $_ eq ".." );
    next if ( $_ =~ /^\d\d\d\d$/ );
    my ($dir, $day_dir, $month_dir) = ($_, $_, $_);
    $day_dir =~ s/(\d\d\d\d)(\d\d)(\d\d)/\1\/\2\/\3/;
    $month_dir =~ s/(\d\d\d\d)(\d\d)(\d\d)/\1\/\2/;
    my $new_day = $d . $day_dir ;
    my $new_month = $d . $month_dir ;
    my $old = $d . $dir ;
    make_path($new_month, {chmod => 0775});
    print "mv $old $new_day\n";
}
closedir $dh;

