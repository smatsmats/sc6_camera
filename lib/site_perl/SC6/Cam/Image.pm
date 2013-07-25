package SC6::Cam::Image;

use strict;
use warnings;
use SC6::Cam::General;
use SC6::Cam::BlueCode;
use SC6::Cam::Overlay;
use Data::Dumper;

sub new {
    my $class = shift;
    my $self = {
        _dt => shift,
        _mode => shift,
        _dryrun => shift,
        _sun => shift,
    };

    # format isn't really used yet, so we just set it staticallyk
    my $format = "orig";

    # these are the files that are saved
    my $image_dir = get_image_dir($self->{_dt}, "orig", $self->{_mode});
    $self->{_output} = $image_dir . "image" . $self->{_dt}->epoch() . "_orig.jpg";
    $image_dir = get_image_dir($self->{_dt}, "50pct", $self->{_mode});
    $self->{_output_50pct} = $image_dir . "image" . $self->{_dt}->epoch() . "_50pct.jpg";

    # these are the files / links used on the web page
    my $www_dir = get_www_dir($format, $self->{_mode});
    $self->{_www_image_orig} = $www_dir . "current_image_orig.jpg";
    $self->{_www_image_25pct} = $www_dir . "current_image_25pct.jpg";
    $self->{_www_image_50pct} = $www_dir . "current_image_50pct.jpg";

    bless $self, $class;
    return $self;
}

sub fetch {
    my ($self) = @_;

    my $d_txt = "";
#    if ( $debug ) {
#        $d_txt = "--verbose --trace-time";
#    }
    my $misc_args = $main::config->{Image}->{Fetch}->{MiscArgs};
    my $auth = $main::config->{Image}->{Fetch}->{Auth};
    my $url = $main::config->{Image}->{Fetch}->{Url};
    my $extra_debug = $main::config->{Image}->{Fetch}->{ExtraDebug};
    my $cmd = $main::config->{Image}->{Fetch}->{Command};

    my $output = $self->{_output};

    my $fetch_cmd = "$cmd $extra_debug $misc_args $auth $url > $output";
    i_do_cmd($self, $fetch_cmd);

    if ( -z $output ) {
        unlink $output or die "Can't unlink $output $!\n";
        $self->{_success} = 0;
    }
    else {
        $self->{_success} = 1;
    }

    return $self->{_success};

}

sub resizes_and_links {
    my ($self) = @_;

    my $output = $self->{_output};
    my $output_50pct = $self->{_output_50pct};
    my $www_image_orig = $self->{_www_image_orig};
    my $www_image_25pct = $self->{_www_image_25pct};
    my $www_image_50pct = $self->{_www_image_50pct};

    my $scale_cmd = "convert -scale 50% $output $output_50pct";
    i_do_cmd($self, $scale_cmd);
    $scale_cmd = "convert -scale 25% $output $www_image_25pct";
    i_do_cmd($self, $scale_cmd);

    if ( -l $www_image_orig ) {
            unlink($www_image_orig) or die "Can't unlink $www_image_orig: $!\n";
    }
    symlink($output, $www_image_orig) or die "Can't symlink $output to $www_image_orig: $!\n";
    if ( -l $www_image_50pct ) {
            unlink($www_image_50pct) or die "Can't unlink $www_image_50pct: $!\n";
    }
    symlink($output_50pct, $www_image_50pct) or die "Can't symlink $output_50pct to $www_image_50pct: $!\n";

}

sub getSun {
    my ($self) = @_;
    
    return($self->{_sun});

}

sub getBluecode {
    my ($self) = @_;
    
    if ( ! $self->{_bc} ) {
        $self->{_bc} = new SC6::Cam::BlueCode($self->{_output});
    }
    return($self->{_bc}->{_bluecode});

}

sub getBluecodes {
    my ($self) = @_;
    
    if ( ! $self->{_bc} ) {
        $self->{_bc} = new SC6::Cam::BlueCode($self->{_output_50pct});
    }
    return( ($self->{_bc}->{_r}, $self->{_bc}->{_g}, $self->{_bc}->{_b}, $self->{_bc}->{_x}, $self->{_bc}->{_lum}) );

}

sub getOutput {
    my ($self) = @_;
    
    return( $self->{_output} );
}

sub getHour {
    my ($self) = @_;
    
    return( $self->{_dt}->hour );
}

sub getMinute {
    my ($self) = @_;
    
    return( $self->{_dt}->minute );
}

sub do_image_overlays {
    my ( $self ) = @_;
    SC6::Cam::Overlay::do_overlays($self);
}

sub i_do_cmd {
    my ($self, $cmd) = @_;
    print $cmd, "\n";
    if ( ! $self->{_dryrun} ) {
        print `$cmd`;
#        print `$cmd 2>&1`;
    }
}

1;  # don't forget to return a true value from the file
