package SC6::Cam::GStore;

use strict;
use warnings;
use Data::Dumper;
use DateTime;
use DateTime::Event::Sunrise;

sub new {
    my $class = shift;
    my $self = {
        _bucket => shift,
        _gsutil => shift,
    };
    bless $self, $class;
    init($self);

    return $self;
}

sub init {
    my ($self ) = @_;
    $self->{_bucket} = $main::config->{GStore}->{ImageBucket};
    $self->{_gsutil} = $main::config->{GStore}->{gsutilPath};

    return($self);
}

sub cp {
    my ($self, $src, $dest_dir) = @_;
    
    if ( ! -f $src ) {
        print "file $src missing\n";
        return 0;
    }

    my $gscmd = $self->{_gsutil} . " cp " . $src . " " . $self->{_bucket} . "/" . $dest_dir;
    print $gscmd, "\n" if ( $main::debug );
    print `$gscmd`;

    return 1;
}

1;  # don't forget to return a true value from the file
