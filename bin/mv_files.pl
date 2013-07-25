#!/usr/bin/perl

my $d = "/data/cam_images/20130204/orig";

opendir(my $dh, $d) || die;

while(readdir $dh) {
    next if ( $_ eq "." );
    next if ( $_ eq ".." );
    next if ( $_ =~ /_orig.jpg/ );
    my $new =  $d . "/" . $_;
    $new =~ s/.jpg$//;
    $new .= "_orig.jpg";
    print "mv $d/$_ $new\n";
#    print `mv $d/$_ $new`;
}
closedir $dh;

