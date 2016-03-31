package SC6::Cam::BlueCode;

use strict;
use warnings;
use DateTime;
use File::Copy;
use GD;

sub new {
    my $class = shift;
    my $self = {
        _fn => shift,
    };

    get_blue($self);

    bless $self, $class;
    return $self;
}


sub get_blue {
    my ($self) = @_;

    my $start_row = $main::config->{BlueCode}->{BlueTest}->{StartRow};
    my $rows = $main::config->{BlueCode}->{BlueTest}->{Rows};
    my $sample = $main::config->{BlueCode}->{Sampling};

    print "file: ", $self->{_fn}, "\n" if ( $main::debug );
    my $image = GD::Image->newFromJpeg($self->{_fn}) or die "Can't open / load ", $self->{_fn}, " $!\n";
    my ($width,$height) = $image->getBounds();
    print "w: ", $width, " h: ", $height, "\n" if ( $main::debug );

    my $cum_new_bc = 0;
    my $cum_bc = 0;
    my $cum_lum = 0;
    my $cum_r = 0;
    my $cum_g = 0;
    my $cum_b = 0;

    for ( my $x=0; $x <= $width; $x += $sample ) {
        for ( my $y = $start_row; $y <= $start_row + $rows; $y += $sample ) {
            my ( $r, $g, $b ) = $image->rgb($image->getPixel($x,$y));
            # looking at the difference between blue and the average of red and green then
            # multiply by the luminosity to give weight to bright images
            #$cum_bc += ($b - ( ($r + $g) / 2)) * ( 2 * ((0.2126*$r) + (0.7152*$g) + (0.0722*$b)));
            # don't use the green value for the difference 
            # because dusk and down can be very green
            $cum_bc += ($b - $r ) * ( 2 * ((0.2126*$r) + (0.7152*$g) + (0.0722*$b)));
            $cum_lum += (0.2126*$r) + (0.7152*$g) + (0.0722*$b);
            $cum_r += $r;
            $cum_g += $g;
            $cum_b += $b;
            # Base BlueCode: $b - ( ($r + $g) / 2);
            # Luminence: (0.2126*$r) + (0.7152*$g) + (0.0722*$b)
            # double the Luminence
            if ( $r >= 32 && $g >= 32 ) {
                $cum_new_bc += ($b - $g ) * ( 2 * ((0.2126*$r) + (0.7152*$g) + (0.0722*$b)));
            }
        }
    }

    my $scaling_factor = $main::config->{BlueCode}->{CodeScaling};
    my $a_w = $cum_bc / ( $width * $rows ) * $scaling_factor;
    my $a_new_w = $cum_new_bc / ( $width * $rows ) * $scaling_factor;
    $cum_r = $cum_r / ( $width * $rows );
    $cum_g = $cum_g / ( $width * $rows );
    $cum_b = $cum_b / ( $width * $rows );
    $cum_lum = $cum_lum / ( $width * $rows );

#    print "Blue code: $a_w\n" if ( $main::debug );
#    print "New Blue code: $a_new_w\n" if ( $main::debug );
#    print "Luminence: $cum_lum\n" if ( $main::debug );
#    print "Cum R: $cum_r\n" if ( $main::debug );
#    print "Cum G: $cum_g\n" if ( $main::debug );
#    print "Cum B: $cum_b\n" if ( $main::debug );

    $self->{_bluecode} = $a_w;
    $self->{_x} = $a_new_w;
    $self->{_r} = $cum_r;
    $self->{_g} = $cum_g;
    $self->{_b} = $cum_b;
    $self->{_lum} = $cum_lum;

    return $self;
}

sub getBluecode {
    my ($self) = @_;
    return $self;
}

END {    # module clean-up code here (global destructor)
    ;
}

1;  # don't forget to return a true value from the file
