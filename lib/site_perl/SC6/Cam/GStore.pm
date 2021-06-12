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
        _bucketshiz => shift,
    };
    bless $self, $class;
    init($self);

    return $self;
}

sub init {
    my ($self ) = @_;
    $self->{_bucket} = $main::config->{BucketShiz}->{ImageBucket};
    $self->{_bucketshiz} = $main::config->{BucketShiz}->{bucketshizPath};

    return($self);
}

sub cp_bucket2bucket {
    my ($self, $src, $dest_dir) = @_;
    
    my $full_src = $src;
    my $full_dest = $dest_dir . "/" . basename($src);

    my $buckcmd = $self->{_bucketshiz} . " --copy --src_name " . $full_src . " --dst_name " . $full_dest;
    print $buckcmd, "\n" if ( $main::debug );
    print `$buckcmd`;

    set_cache_control($self, $full_dest);
}

sub cp_fs2bucket {
    my ($self, $src, $dest_dir) = @_;
    
    if ( ! -f $src ) {
        print "file $src missing\n";
        return 0;
    }

    my $full_src = $src;
    my $full_dest = $dest_dir . "/" . basename($src);

    my $buckcmd = $self->{_bucketshiz} . " --upload --file " . $full_src . " --dst_name " . $full_dest;
    print $buckcmd, "\n" if ( $main::debug );
    print `$buckcmd`;

    set_cache_control($self, $full_dest);
}

sub set_cache_control {
    my ($self, $full_dest) = @_;

    my $f = basename($full_dest);
    my $cache_timeout = $main::config->{BucketShiz}->{Cache}->{MaxAge}->{$f};
    my $cache_control = $main::config->{BucketShiz}->{Cache}->{CacheControl};

    my $cachecontrol_val = "'" . $cache_control . ", max-age=" . $cache_timeout . "'";

    my $buckcmd = $self->{_bucketshiz} . " --blob_name " . $full_dest . " --set_cachecontrol --cachecontrol " . $cachecontrol_val;
    print $buckcmd, "\n" if ( $main::debug );
    print `$buckcmd`;

}

1;  # don't forget to return a true value from the file
