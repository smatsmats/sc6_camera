package SC6::Cam::WX;

use strict;
use warnings;
use Data::Dumper;
use DateTime;
use DateTime::Event::Sunrise;

use constant HOUR_SECS => ( 60 * 60 );

sub new {
    my $class = shift;
    my $self = {
        _dt => shift,
    };
    bless $self, $class;
    $self = current_values($self);

    return $self;
}

sub current_values {
    my ($self) = @_;

    my $rrdtool = $main::config->{WX}->{rrdtool};
    my $rrdfile = $main::config->{WX}->{RRD_File};

    my $cmd = $rrdtool . " lastupdate " . $rrdfile;

    my @res = `$cmd`;
    
    # results from lastupdate are two lines, arguments and values.  
    # values is prefixed by the timestamp. 
    my @args = split " ", $res[0];
    my @vals = split " ", $res[2];
    my %h;
    for (my $i = 0; $i < $#args + 1; $i++) {
        $h{$args[$i]} = $vals[$i+1];
    }
    $self->{_current} = \%h;
    return($self);
}

sub rain_today
{
    my ($self) = @_;
    
    my $rain_ds = $main::config->{WX}->{Dataset}->{Rain};
    return $self->{_current}->{$rain_ds};
}

1;  # don't forget to return a true value from the file
