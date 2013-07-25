package SC6::Cam::Config;

use strict;
use warnings;
use YAML;
use YAML::Tiny;
use Data::Dumper;

sub new {
    my $class = shift;
    my $self = {
        _config => shift,
        _debug  => shift,
    };
    my $config_file = "/usr/local/cam/conf/config.yml";
    my $in = YAML::Tiny->read( $config_file );
    $self->{_config} = $in->[0]->{Root1};
    if ( ! $self->{_config} ) {
        print "failed to read $config_file $! ", YAML::Tiny->errstr, "\n";
        exit();
    }
    $self->{_debug} = $self->{_config}->{'Debug'}->{'Level'};
#    $self->{_debug} = $self->{_config}->[0]->{'Debug'}->{'Level'};

    my $debug_dump_config = $self->{_config}->{'Debug'}->{'DumpConfig'};
    if ( $self->{_debug} >= $debug_dump_config ) {
        print Dumper($self->{_config});
    }

    bless $self, $class;
    return $self;
}

sub getConfig {
    my ($self ) = @_;

    return $self->{_config};
}

sub getDebug {
    my ($self ) = @_;

    return $self->{_debug};
}

1;  # don't forget to return a true value from the file
