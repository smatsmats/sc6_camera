package SC6::Cam::Config;

use strict;
use warnings;
use YAML;
use YAML::Tiny;
use Data::Dumper;

sub new {
    my $class = shift;
    my $self = {
        _config_file => shift,
        _config => shift,
        _debug  => shift,
        _in  => shift,
    };
    my $in = YAML::Tiny->read( $self->{_config_file} );
    $self->{_in} = $in;
    $self->{_config} = $in->[0]->{Root1};
    if ( ! $self->{_config} ) {
        print "failed to read $self->{_config_file} $! ", YAML::Tiny->errstr, "\n";
        exit();
    }
    $self->{_debug} = $self->{_config}->{'Debug'}->{'Level'};

    if ( $self->{_debug} >= $self->{_config}->{'Debug'}->{'DumpConfig'} ) {
        print "read config:", Dumper($self->{_config});
    }

    bless $self, $class;
    return $self;
}

sub getConfig {
    my ($self ) = @_;

    return $self->{_config};
}

sub writeConfig {
    my ($self, $old ) = @_;

    # replace config
    $self->{_in}->[0]->{Root1} = $old;
    if ( $self->{_debug} >= $self->{_config}->{'Debug'}->{'DumpConfig'} ) {
        print "going to write:", Dumper($self->{_in});
    }
    # write new config
    if ( ! $self->{_in}->write( $self->{_config_file} ) ) {
        die "errors writing ", $self->{_config_file}, " : $!\n";
    }
}

sub getDebug {
    my ($self ) = @_;

    return $self->{_debug};
}

1;  # don't forget to return a true value from the file
