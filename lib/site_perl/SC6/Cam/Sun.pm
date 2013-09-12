package SC6::Cam::Sun;

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
        _longitude => shift,
        _latitude => shift,
        _angle_nautical => shift,
        _angle_civil => shift,
        _angle_horizon => shift,
        _iteration => shift,
    };
    bless $self, $class;
    init($self);

    return $self;
}

sub init {
    my ($self ) = @_;
    $self->{_dt} = DateTime->now(  time_zone => $main::config->{'General'}->{'Timezone'} );
    $self->{_longitude} = $main::config->{Sun}->{Long};
    $self->{_latitude} = $main::config->{Sun}->{Lat};
    $self->{_angle_nautical} = $main::config->{Sun}->{AngleNautical};
    $self->{_angle_civil} = $main::config->{Sun}->{AngleCivil};
    $self->{_angle_horizon} = $main::config->{Sun}->{AngleHorizon};
    $self->{_iteration} = $main::config->{Sun}->{Iteration};
    $self->{_sun_message} = "Sunrise / Sunset times:\n";

    my $sunrise_span = DateTime::Event::Sunrise ->new (
                        longitude => $self->{_longitude},
                        latitude => $self->{_latitude},
                        altitude => $self->{_angle_nautical},
                        iteration => $self->{_iteration},
                   );
    my $both_times = $sunrise_span->sunrise_sunset_span($self->{_dt});
    $self->{_sun_message} .= "Nautical Dawn is: " . $both_times->start->datetime . "\n";
    $self->{_sun_message} .= "Nautical Twilight is: " . $both_times->end->datetime . "\n";
    $self->{_naut_dawn} = $both_times->start;
    $self->{_naut_dusk} = $both_times->end;

    $sunrise_span = DateTime::Event::Sunrise ->new (
                        longitude => $self->{_longitude},
                        latitude => $self->{_latitude},
                        altitude => $self->{_angle_civil},
                        iteration => $self->{_iteration},
                   );
    $both_times = $sunrise_span->sunrise_sunset_span($self->{_dt});
    $self->{_sun_message} .= "Civil Dawn is: " . $both_times->start->datetime . "\n";
    $self->{_sun_message} .= "Civil Twilight is: " . $both_times->end->datetime . "\n";
    $self->{_civi_dawn} = $both_times->start;
    $self->{_civi_dusk} = $both_times->end;

    $sunrise_span = DateTime::Event::Sunrise ->new (
                        longitude => $self->{_longitude},
                        latitude => $self->{_latitude},
                        altitude => $self->{_angle_horizon},
                        iteration => $self->{_iteration},
                   );
    $both_times = $sunrise_span->sunrise_sunset_span($self->{_dt});
    $self->{_sun_message} .= "Sunrise is: " . $both_times->start->datetime . "\n";
    $self->{_sun_message} .= "Sunset is: " . $both_times->end->datetime . "\n";
    $self->{_sunrise} = $both_times->start;
    $self->{_sunset} = $both_times->end;

#    print $self->{_sun_message} if ( $main::debug );

    return($self);
}

sub sun_message {
    my ($self) = @_;
    return $self->{_sun_message};
}

sub check4newday {
    my ($self, $dt) = @_;

    my $old_dt = $self->{_dt};
    if ( $dt->ymd ne $old_dt->ymd ) {
        init($self);
    }
    return($self);
}

sub is_sun {
    my ($self, $dt) = @_;
    
    check4newday($self, $dt);

    my $up = $self->{_naut_dawn};
    my $down = $self->{_naut_dusk};

    if ( $dt->epoch() >= $up->epoch() 
      && $dt->epoch() <= $down->epoch() ) {
        return 1;
    }
    else {
        return 0;
    }
}

sub start_time {
    my ($self) = @_;

    return $self->{_naut_dawn};
}

sub end_time {
    my ($self) = @_;

    return $self->{_naut_dusk};
}

sub is_hour_after_dusk {
    my ($self, $dt) = @_;

    my $up = $self->{_naut_dawn};
    my $down = $self->{_naut_dusk};

    if ( $dt->epoch() >= $down->epoch() 
      && $dt->epoch() <= $down->epoch() + HOUR_SECS ) {
        return 1;
    }
    else {
        return 0;
    }
}

1;  # don't forget to return a true value from the file
