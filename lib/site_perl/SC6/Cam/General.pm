package SC6::Cam::General;

use strict;
use warnings;
use DateTime;
use DateTime::Event::Sunrise;
use GD;
use Data::Dumper;

BEGIN {
        require Exporter;

        # set the version for version checking
        our $VERSION     = 1.00;

        # Inherit from Exporter to export functions and variables
        our @ISA         = qw(Exporter);

        # Functions and variables which are exported by default
        our @EXPORT      = qw(get_image_dir get_video_dir get_video_file get_www_dir do_cmd);

        # Functions and variables which can be optionally exported
        our @EXPORT_OK   = qw($Var1 %Hashit func3);
}


# file-private lexicals go here, before any functions which use them
my $priv_var    = '';
my %secret_hash = ();
use constant HOUR_SECS => ( 60 * 60 );

sub get_image_dir {
    my ($ldt, $format, $mode) = @_;

    my $ci = $main::config->{Directories}->{cam_images}->{$mode};
    if ( ! $ci ) {
        print "missing correct mode ('test', 'prod', etc.).  got $mode\n";
        return;
    }
    
    $ci .= sprintf ("%4d%02d%02d/", $ldt->year, $ldt->month, $ldt->day);
    mkdir ($ci, 0775) or die "can't make dir $ci: $!\n" unless ( -d $ci );
    my $o = $ci . $format . "/" ;
    mkdir ($o, 0775) or die "can't make dir $o: $!\n" unless ( -d $o );

    return $o;
}

sub get_www_dir {
    my ($format, $mode) = @_;

    print "****** got $mode\n";
    my $ci = $main::config->{Directories}->{www}->{$mode};
    if ( ! $ci ) {
        print "missing correct mode ('test', 'prod', etc.).  got $mode\n";
        return;
    }
    
    mkdir ($ci, 0775) or die "can't make dir $ci: $!\n" unless ( -d $ci );

    return $ci;
}

sub get_video_dir {
    my ($dt, $format, $mode) = @_;

    my $ci = $main::config->{Directories}->{video}->{$mode};
    if ( ! $ci ) {
        print "missing correct mode ('test', 'prod', etc.).  got $mode\n";
        return;
    }
    
    mkdir ($ci, 0775) or die "can't make dir $ci: $!\n" unless ( -d $ci );

    return $ci;
}

sub get_video_file {
    my ($dt, $format, $postfix, $mode) = @_;
    
    return get_video_dir($dt, $format, $mode) . "output_" . $format . "." . $postfix;
}

sub do_cmd {
    my ($cmd, $dryrun) = @_;
    print $cmd, "\n";
    if ( ! $dryrun ) {
        print `$cmd`;
#        print `$cmd 2>&1`;
    }
}

END {    # module clean-up code here (global destructor)
    ;
}

1;  # don't forget to return a true value from the file
