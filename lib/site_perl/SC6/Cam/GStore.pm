package SC6::Cam::GStore;

use strict;
use warnings;
use Data::Dumper;
use DateTime;
use DateTime::Event::Sunrise;
use File::Basename;

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
    $self->{_url} = $main::config->{GStore}->{URL_Prefix};

    return($self);
}

sub web_url {
    my ($self, $dir, $file) = @_;

    my $url = $self->{_url} . $self->{_bucket} . "%2F" . $dir . "%2F" . basename($file);
    return $url;
}

sub cp {
    my ($self, $src, $dest_dir) = @_;
    
    if ( ! -f $src ) {
        print "file $src missing\n";
        return 0;
    }

#gsutil -h "Content-Type:text/html" \
#       -h "Cache-Control:public, max-age=3600" cp -r images \
#       gs://bucket/images
    
    # get cache timeout
    my $file = basename($src);
print $file, "\n";
    my $cache_timeout = $main::config->{GStore}->{CacheTimeout}->{$file};

    my $cache_header = " -h \"Cache-Control:public, max-age=" . $cache_timeout . "\" ";
    my $full_dest = "gs://" . $self->{_bucket} . "/" . $dest_dir;

    my $gscmd = $self->{_gsutil} . $cache_header . " cp " . $src . " " . $full_dest;
    print $gscmd, "\n" if ( $main::debug );
    print `$gscmd`;

    

    return 1;
}

1;  # don't forget to return a true value from the file
