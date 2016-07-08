#!/usr/bin/perl

my $rut = "/home/willey/sc6_camera/data/cam_images";

opendir my $dh, $rut or die "Could not open '$rut' for reading: $!\n";
while (my $thing = readdir $dh) {

    if ($thing eq '.' or $thing eq '..') {
        next;
    }
    if ($thing eq 'on_data' ) {
        next;
    }
    my $dd = $rut . "/" . $thing;
    my $public = $dd . "/public";
    my $orig = $dd . "/orig";
#    print $dd, "\n";
    if ( ! -e $public ) { 
        print "going to ln -s $orig $public\n";
        symlink($orig, $public) or die "Can't symlink($orig, $public): $!\n";
    }
    
}

