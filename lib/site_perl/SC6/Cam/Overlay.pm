package SC6::Cam::Overlay;

use strict;
use warnings;
use DateTime;
use GD;
use GD::Graph::hbars;
use SC6::Cam::WX;
use Graphics::ColorNames 2.10;
use Data::Dumper;

BEGIN {
        require Exporter;

        # set the version for version checking
        our $VERSION     = 1.00;

        # Inherit from Exporter to export functions and variables
        our @ISA         = qw(Exporter);

        # Functions and variables which are exported by default
        our @EXPORT      = qw(do_overlays add_clock);

        # Functions and variables which can be optionally exported
        our @EXPORT_OK   = qw(sun_times $Var1 %Hashit func3);
}

# file-private lexicals go here, before any functions which use them
use constant PI => 4 * atan2(1, 1);

sub do_overlays {
    my ($cim) = @_;

    my $image_file = $cim->getOutput();
    my $minute = $cim->getMinute();
    my $hour = $cim->getHour();
    my ($r, $g, $b, $x, $lum) = $cim->getBluecodes();
    my $bluecode = $cim->getBluecode();
    my $s = $cim->getSun();

    if ( lc($main::config->{Overlay}->{Clock}->{Overlay}) ne "true" &&
         lc($main::config->{Overlay}->{ColorGraph}->{Overlay}) ne "true" &&
         lc($main::config->{Overlay}->{WX}->{Overlay}) ne "true" ) {
        return 
    }

    # load the picture image file
    my $main = GD::Image->newFromJpeg($image_file, 1);
    if ( ! $main ) {
        die "Can't make an image from $image_file\n";
        return;
    }
    my ($w, $h) = $main->getBounds();

    # get the clock
    if ( lc($main::config->{Overlay}->{Clock}->{Overlay}) eq "true" ) {
        my $clock_overlay = add_clock($hour, $minute);
        my ($cw,$ch) = $clock_overlay->getBounds();
        my ($clock_x, $clock_y) = overlay_location("Clock", $w, $h, $cw, $cw);
        print "Copy clock to coordinates: $clock_x,$clock_y\n" if ( $main::debug );
        $main->copy($clock_overlay,$clock_x,$clock_y,0,0,$cw,$ch);
    }

    # get the colorGraph
    if ( lc($main::config->{Overlay}->{ColorGraph}->{Overlay}) eq "true" ) {
        my $cg_overlay = add_colorgraph($r, $g, $b, $x, $bluecode, $lum);
        my ($cgw,$cgh) = $cg_overlay->getBounds();
        my ($cg_x, $cg_y) = overlay_location("ColorGraph", $w, $h, $cgw, $cgh);
        print "Copy ColorGraph to coordinates: $cg_x,$cg_y\n" if ( $main::debug );
        $main->copy($cg_overlay,$cg_x,$cg_y,0,0,$cgw,$cgh);
    }

    # get the WX graphs
    if ( lc($main::config->{Overlay}->{WX}->{Overlay}) eq "true" ) {
        my $overlay = add_wx_overlays($s, $w, $h);
        my ($o_w,$o_h) = $overlay->getBounds();
        my ($o_x, $o_y) = overlay_location("WX", $w, $h, $o_w, $o_h);
        # a instead of doing an overlay create a new image with the graphs appended
        my $new_main = GD::Image->new($w, $h + $o_h, 1);
        $new_main->copy($main,0,0,0,0,$w,$h);
        print "Appending WX Graphs\n" if ( $main::debug );
        $new_main->copy($overlay,0,$h,0,0,$o_w,$o_h);
        $main = $new_main;
    }

    open OUT, ">$image_file" or die "Can't open $image_file for writing: $!\n";
    binmode OUT;
    print OUT $main->jpeg;
    close OUT;
}

sub add_clock {
    my ($hour, $min) = @_;

    my $width = $main::config->{Overlay}->{Clock}->{Width};
    my $height = $main::config->{Overlay}->{Clock}->{Height};
    my $x_border = $main::config->{Overlay}->{Clock}->{XBorder};
    my $y_border = $main::config->{Overlay}->{Clock}->{YBorder};

    # center
    my $cx = $width / 2;
    my $cy = $height / 2;

    # thickness 
    my $t = $main::config->{Overlay}->{Clock}->{LineWeight};

    # create a new image
    my $im = new GD::Image($width,$height);

    # get colors
    my $po = new Graphics::ColorNames(qw( X ));
    my @fg_color = $po->rgb(lc($main::config->{Overlay}->{Clock}->{FGColor}));
    my @bg_color = $po->rgb(lc($main::config->{Overlay}->{Clock}->{BGColor}));

    # first color allocated is background color
    my $im_bg_color = $im->colorAllocate(@bg_color);
    my $im_fg_color = $im->colorAllocate(@fg_color);

    # radiuses
    my $hradius = $width / 4;
    my $mradius = ($width / 2) * .70;

    # make the background transparent and interlaced
    $im->transparent($im_bg_color);
    $im->interlaced('true');
    $im->setThickness($t);

    # Create a brush with a round end
    my $round_brush = new GD::Image($t*2,$t*2);
    # first color allocated is background color
    my $rb_bg_color = $round_brush->colorAllocate(@bg_color);
    my $rb_fg_color = $round_brush->colorAllocate(@fg_color);
    $round_brush->transparent($rb_bg_color);

    $round_brush->arc($t,$t,$t,$t,0,360,$rb_fg_color); 
    
    # if you need to see the brush, uncomment this
    #$im->copy($round_brush,0,0,0,0,$t*2,$t*2);

    # Set the brush
    $im->setBrush($round_brush);

    # maybe antialiased
    $im->setAntiAliased($im_fg_color);

    # cicle
    $im->arc($cx,$cy,$width - $t*2 - $x_border,$height - $t*2 - $y_border,0,360,gdAntiAliased);

    # minute hand
    my ($mex, $mey) = minute_point($min, $cx, $cy, $mradius, $main::debug);
    $im->line($cx,$cy,$mex,$mey,gdBrushed);

    # hour hand
    my ($hex, $hey) = hour_point($hour, $min, $cx, $cy, $hradius, $main::debug);
    $im->line($cx,$cy,$hex,$hey,gdBrushed);


    if ( lc($main::config->{Overlay}->{Clock}->{WriteImage}) eq "true" ) {
        my $file = $main::config->{Overlay}->{Clock}->{ImageFile};
        open OUT, ">$file" or die "Can't open $file for writing: $!\n";
        binmode OUT;
        print OUT $im->jpeg;
        close OUT;
    }

    return($im);
}

sub add_wx_overlays {
    my ($s, $main_w, $main_h) = @_;

    my $wx = SC6::Cam::WX->new();
    print "rain today: ", $wx->rain_today, "\n";

    my $indi_width = $main::config->{Overlay}->{WX}->{IndividualWidth};
    my $indi_height = $main::config->{Overlay}->{WX}->{IndividualHeight};

    my @graphs_maybe = ( "TDW", "Rain", "Pressure", "Wsp", "Dir", "Solar");
    my @graphs;
    foreach my $g ( @graphs_maybe ) {
#        next if ( $g eq "Rain" && $wx->rain_today == 0 );
        push @graphs, wx_graph($g, $s, $indi_width, $indi_height);
    }

    my $im = new GD::Image($indi_width,$indi_height * ($#graphs+1));
    # allocate some colors
    my $white = $im->colorAllocate(255,255,255);
    my $black = $im->colorAllocate(0,0,0);
    # make the background transparent and interlaced
    $im->transparent($white);

    my $upper_left_x = 0;
    foreach my $o ( @graphs ) {
        $im->copy($o,0,$upper_left_x,0,0,$indi_width,$indi_height);
        $upper_left_x += $indi_height;
    }

    if ( lc($main::config->{Overlay}->{WX}->{WriteImage}) eq "true" ) {
        my $file = $main::config->{Overlay}->{WX}->{ImageFile};
        open OUT, ">$file" or die "Can't open $file for writing: $!\n";
        binmode OUT;
        print OUT $im->jpeg;
        close OUT;
    }

    return($im);
}

sub add_colorgraph {
    my ($r, $g, $b, $x, $bluecode, $lum) = @_;

    my @data = ( 
        ["BC","Lum","R","G","B","X"],
        [$bluecode, $lum, $r, $g, $b, $x]
    );
    my $width = $main::config->{Overlay}->{ColorGraph}->{Width};
    my $height = $main::config->{Overlay}->{ColorGraph}->{Height};
    my $x_border = $main::config->{Overlay}->{ColorGraph}->{XBorder};
    my $y_border = $main::config->{Overlay}->{ColorGraph}->{YBorder};

    # center
    my $cx = $width / 2;
    my $cy = $height / 2;

    # thickness 
    my $t = $main::config->{Overlay}->{ColorGraph}->{LineWeight};

    my $graph = GD::Graph::hbars->new($width,$height);

#    $graph->set( dclrs => [ qw($main::config->{Overlay}->{ColorGraph}->{FGColor} $main::config->{Overlay}->{ColorGraph}->{LumColor} red green blue $main::config->{Overlay}->{ColorGraph}->{XColor}) ] );
    $graph->set( dclrs => [ qw(pink yellow red green blue white) ]);
    $graph->set( 
      cycle_clrs           => 1,
      y_min_value       => 0,
      show_values       => 1,
      values_format       => "%d",
    ) or die $graph->error;
    my $im = $graph->plot(\@data);

    if ( lc($main::config->{Overlay}->{ColorGraph}->{WriteImage}) eq "true" ) {
        my $file = $main::config->{Overlay}->{ColorGraph}->{ImageFile};
        open OUT, ">$file" or die "Can't open $file for writing: $!\n";
        binmode OUT;
        print OUT $im->jpeg;
        close OUT;
    }

    return($im);
}

sub minute_point {
    my ($minute, $xcenter, $ycenter, $mradius) = @_;

    my $x = $xcenter + ($mradius*(sin(2*PI*($minute/60))));
    my $y = $ycenter + (-1*$mradius*(cos(2*PI*($minute/60))));
#    print "minute hand x: $x = $xcenter + ($mradius*(sin(2*PI*($minute/60))))\n" if ( $main::debug );
#    print "minute hand y: $y = $ycenter + (-1*$mradius*(cos(2*PI*($minute/60))))\n" if ( $main::debug );

    return($x, $y);
}

sub hour_point {
    my ($hour, $minute, $xcenter, $ycenter, $hradius) = @_;

    my $totalSeconds = (3600*$hour + 60*$minute) / 43200;
    my $x = $xcenter + ($hradius*(sin(2*PI*$totalSeconds)));
    my $y = $ycenter + (-1*$hradius*(cos(2*PI*$totalSeconds)));
#    print "hour hand x: $x = $xcenter + ($hradius*(sin(2*PI*$totalSeconds)))\n" if ( $main::debug );
#    print "hour hand y: $y = $ycenter + (-1*$hradius*(cos(2*PI*$totalSeconds)))\n" if ( $main::debug );

    return($x, $y);
}

sub overlay_location {
    my ($type, $main_x, $main_y, $ox, $oy) = @_;

    # configuration location of ColorGraph
    my $config_x = lc($main::config->{Overlay}->{$type}->{XLocation});
    my $config_y = lc($main::config->{Overlay}->{$type}->{YLocation});
    
    # translate natural language config options
    $config_x = 0 if ( $config_x eq "left" );
    $config_x = 100 if ( $config_x eq "right" );
    $config_y = 0 if ( $config_y eq "top" );
    $config_y = 100 if ( $config_y eq "bottom" );

    # image location
    my $x = ($main_x - $ox) * $config_x / 100;
    my $y = ($main_y - $oy) * $config_y / 100;

    return ($x, $y);
}

sub wx_graph {
    my ($attr, $s, $width, $height) = @_;
    
    # get time ranges and image size
    my $length_day = $s->{naut_dusk}->epoch() - $s->{naut_dawn}->epoch();
    my $dt = DateTime->now(  time_zone => $main::config->{'General'}->{'Timezone'} );
    my $day_so_far = $dt->epoch() - $s->{naut_dawn}->epoch();
    print "length of day: $length_day, so far $day_so_far, ", ($day_so_far / $length_day * 100), "% of the way there\n" if ( $main::debug );
    my $rrd_width = $width * ($day_so_far / $length_day);

    my $rrdtool = $main::config->{WX}->{rrdtool};
    my $outfile = $main::config->{WX}->{$attr}->{ImageFile};
    my $title = "\"" . $attr . "\"";
    my $vlabel = "\"" . $main::config->{WX}->{$attr}->{VLabel} . "\"";
    my $dd = $main::config->{WX}->{$attr}->{DD};
    my $rrd_args = $main::config->{WX}->{$attr}->{RRDOtherArgs};
  
    my $cmd = "$rrdtool graph $outfile --no-legend --full-size-mode --units-exponent 0 -E -a PNG --alt-y-grid -v $vlabel -w $rrd_width -h $height -s -$day_so_far $rrd_args $dd";
    print $cmd, "\n" if ( $main::debug );
    print `$cmd`;

    # create a new full sized image
    my $im = new GD::Image($width,$height);
    # allocate some colors
    my $white = $im->colorAllocate(255,255,255);
    my $black = $im->colorAllocate(0,0,0);       
    # make the background transparent and interlaced
    $im->transparent($white);

    # read back in the rrd graph and copy
    my $rrd_im = GD::Image->newFromPng($outfile);
    $im->copy($rrd_im,0,0,0,0,$rrd_width,$height);

    return $im; 
}

END {    # module clean-up code here (global destructor)
    ;
}

1;  # don't forget to return a true value from the file
