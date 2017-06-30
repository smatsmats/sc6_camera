#!/usr/bin/perl

use File::Find;

my $rut_base = "/usr/local/cam/data/cam_images/";
my $rut = $rut_base . "/";

find(\&wanted, $rut);

# handler called for each file from Find
sub wanted {

    return if ( $_ ne "stash" );  # skip non-xml
    my $current = $File::Find::name . "/current.jpg";
    if ( -f $current ) {
#        print "$current exists, skipping\n";
        return;
    }
    print $File::Find::name, "\n";
    opendir(my $dir, $File::Find::name) || die "Can't open $File::Find::name $!\n";
    my @dir_list = readdir($dir);
    closedir($dir);
    my $brightest = 0;
    foreach my $d ( @dir_list ) {
        $d =~ s/^([0-9]+\.[0-9]+)/$1/;
#        print $d, "\n";
        if ( $d > $brightest ) {
            $brightest = $d;
        }
    }
    my @sorted = sort @dir_list;
    $b_file = $File::Find::name . "/" . $brightest;
    print "brightest $brightest\n";
    my $link_dest = readlink($b_file);
    if ( ! -f $link_dest ) {
        print "link dest missing: $link_dest\n";
        my $new_date = $link_dest;
        $new_date =~ s/$rut_base([0-9]{8})(.*)$/$1/;
        my $remainder = $2;
        $new_date =~ s/(\d\d\d\d)(\d\d)(\d\d)/$1\/$2\/$3/;
        my $new_dest =  $rut_base . $new_date . $remainder;
        print "new link dest : $new_dest\n";
        if ( ! -f $new_dest ) {
            print "NEW link dest missing: $new_dest\n";
            exit;
        }
        
        #replace link
        print "new link $new_dest to $b_file\n";
        if ( -l $b_file ) {
            unlink($b_file) or die "Can't unlink $b_file: $!\n";
        }
        symlink($new_dest, $b_file) or die "Can't symlink $new_dest to $b_file: $!\n";
        $link_dest = $new_dest;
    }
    print "current link $link_dest to $current\n";
    symlink($link_dest, $current) or die "Can't symlink $link_dest to $current: $!\n";

}

#opendir my $dh, $rut or die "Could not open '$rut' for reading: $!\n";
#while (my $thing = readdir $dh) {
#
#    if ($thing ne 'stash' ) {
#    }
#    
#    print $dd, "<>", $thing, "\n";
#    next;
#    if ( ! -e $public ) { 
#        print "going to ln -s $orig $public\n";
#        symlink($orig, $public) or die "Can't symlink($orig, $public): $!\n";
#    }
    
#}

