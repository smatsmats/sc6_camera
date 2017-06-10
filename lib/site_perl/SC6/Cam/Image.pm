package SC6::Cam::Image;

use strict;
use warnings;
use SC6::Cam::General;
use SC6::Cam::BlueCode;
use SC6::Cam::Overlay;
use SC6::Cam::GStore;
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

    # public version of image (with mask) saved for one day so we can make video
    my $public_image_dir = get_image_dir($self->{_dt}, "public", $self->{_mode});
    $self->{_public_output} = $public_image_dir . "image" . $self->{_dt}->epoch() . "_orig.jpg";
    $public_image_dir = get_image_dir($self->{_dt}, "public_50pct", $self->{_mode});
    $self->{_public_output_50pct} = $public_image_dir . "image" . $self->{_dt}->epoch() . "_50pct.jpg";
    
    # these are the files / links used on the web page
    my $www_dir = get_www_dir($format, $self->{_mode});
    my $www_public_dir = get_www_public_dir($format, $self->{_mode});
    $self->{_www_image_orig} = $www_dir . $main::config->{Image}->{File}->{orig};
    $self->{_www_image_50pct} = $www_dir . $main::config->{Image}->{File}->{'50pct'};
    $self->{_www_public_image_orig} = $www_public_dir . $main::config->{Image}->{File}->{orig};
    $self->{_www_public_image_50pct} = $www_public_dir . $main::config->{Image}->{File}->{'50pct'};

    $self->{_public_mask} = load_privacy_mask();

    bless $self, $class;
    return $self;
}

sub load_privacy_mask {
    if ( lc($main::config->{Public}->{Enable}) ne "true" ) {
        return undef;
    }

    my $mask_file = $main::config->{Public}->{MaskFile};
    my $mask_image = GD::Image->newFromPng($mask_file, 1);
    if ( ! $mask_image ) {
        die "Can't make an image from $mask_file\n";
    }
    return $mask_image;
}

sub fetch {
    my ($self) = @_;

    my $first_args = $main::config->{Image}->{Fetch}->{FirstArgs};
    my $middle_args = $main::config->{Image}->{Fetch}->{MiddleArgs};
    my $final_args = $main::config->{Image}->{Fetch}->{FinalArgs};
    my $extra_debug = $main::config->{Image}->{Fetch}->{ExtraDebug};
    my $cmd = $main::config->{Image}->{Fetch}->{Command};

    my $output = $self->{_output};

    my $fetch_cmd = "$cmd $extra_debug $first_args $middle_args $final_args $output";
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

    my $output_orig = $self->{_output};
    my $output_50pct = $self->{_output_50pct};
    my $www_image_orig = $self->{_www_image_orig};
    my $www_image_50pct = $self->{_www_image_50pct};
    my $public_output_orig = $self->{_public_output};
    my $public_output_50pct = $self->{_public_output_50pct};
    my $www_public_image_orig = $self->{_www_public_image_orig};
    my $www_public_image_50pct = $self->{_www_public_image_50pct};

    my $scale_cmd = "convert -scale 50% $output_orig $output_50pct";
    i_do_cmd($self, $scale_cmd);
    $scale_cmd = "convert -scale 50% $public_output_orig $public_output_50pct";
    i_do_cmd($self, $scale_cmd);
   

    if ( -l $www_image_50pct ) {
            unlink($www_image_50pct) or die "Can't unlink $www_image_50pct: $!\n";
    }
    symlink($output_50pct, $www_image_50pct) or die "Can't symlink $output_50pct to $www_image_50pct: $!\n";
    if ( -l $www_image_orig ) {
            unlink($www_image_orig) or die "Can't unlink $www_image_orig: $!\n";
    }
    symlink($output_orig, $www_image_orig) or die "Can't symlink $output_orig to $www_image_orig: $!\n";
    if ( -l $www_public_image_50pct ) {
            unlink($www_public_image_50pct) or die "Can't unlink $www_public_image_50pct: $!\n";
    }
    symlink($public_output_50pct, $www_public_image_50pct) or die "Can't symlink $public_output_50pct to $www_public_image_50pct: $!\n";
    if ( -l $www_public_image_orig ) {
            unlink($www_public_image_orig) or die "Can't unlink $www_public_image_orig: $!\n";
    }
    symlink($public_output_orig, $www_public_image_orig) or die "Can't symlink $public_output_orig to $www_public_image_orig: $!\n";

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

sub getPublicOutputFile {
    my ($self) = @_;
    
    return( $self->{_public_output} );
}

sub getPublicOutputFile_50pct {
    my ($self) = @_;
    
    return( $self->{_public_output_50pct} );
}

sub getPublicVersion {
    my ($self) = @_;
    return $self->{_public_version};
}

sub setPublicVersion {
    my ($self, $pub) = @_;
    $self->{_public_version} = $pub;
}

sub getPublicWWWFile {
    my ($self) = @_;
    
    return( $self->{_www_public_image_orig} );
}

sub getPublicWWWFile_50pct {
    my ($self) = @_;
    
    return( $self->{_www_public_image_50pct} );
}

sub getOutputFile {
    my ($self) = @_;
    
    return( $self->{_output} );
}

sub getPublicMask {
    my ($self) = @_;

    return ( $self->{_public_mask} );
}

sub getHour {
    my ($self) = @_;
    
    return( $self->{_dt}->hour );
}

sub getMinute {
    my ($self) = @_;
    
    return( $self->{_dt}->minute );
}

sub make_public_version {
    my ( $self ) = @_;
    SC6::Cam::Overlay::do_public_version($self);
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
