package SC6::Cam::Config;

use strict;
use warnings;
use YAML;
use YAML::Tiny;
use Data::Dumper;
use Hash::Merge::Simple qw/ merge /;

sub new {
    my $class = shift;
    my $self = {
        _config_file => shift,
        _mode => shift,
        _config => shift,
        _debug  => shift,
        _in  => shift,
    };
    
    # makde sure we hav a config file
    if ( ! -f $self->{_config_file} ) {
        print "Config file:", $self->{_config_file}, " does not exist\n";
        exit(1);
    }

    # default to Prod
    if ( ! $self->{_mode} ) {
        $self->{_mode} = "Prod";
    }

    # load base tree
    my $in = YAML::Tiny->read( $self->{_config_file} );
    $self->{_in} = $in;
    $self->{_config} = $in->[0]->{$self->{_mode}};

    # make sure we got something
    if ( ! $self->{_config} ) {
        print "failed to read $self->{_config_file} and find ", $self->{_mode}, ", tree $! ", YAML::Tiny->errstr, "\n";
        exit();
    }

    # see if this config tree is templated upon another
    if ( $self->{_config}->{'Config'}->{'Template'} ) {
        my $template = $self->{_config}->{'Config'}->{'Template'};
        if ( ! defined $in->[0]->{$template} ) {
            print "asked to load config template of $template that doesn't exist\n";
            exit(1); 
        }
        my $new_config = merge($in->[0]->{$template}, $self->{_config});
        $self->{_config} = $new_config;
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
    $self->{_in}->[0]->{Prod} = $old;
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
