package SC6::Cam::BlueCodeState;

use strict;
use warnings;
use DateTime;
use File::Copy;
use GD;
use SC6::Cam::General;
use SC6::Cam::GStore;

sub new {
    my $class = shift;
    my $self = { };

    prime($self);

    bless $self, $class;
    return $self;
}

sub checkBluecode {
    my ($self, $new_image) = @_;

    my $new_bluecode = $new_image->getBluecode();
    if ( $new_bluecode > $self->{_bluecode} ) {
        print "new bluecode: $new_bluecode old: ", $self->{_bluecode}, "\n";
        my $www_image_50pct = $new_image->{_www_image_50pct};
        my $www_image_orig = $new_image->{_www_image_orig};
        $self->{_bluecode} = $new_bluecode;
        save_is_blueist($self, $www_image_50pct, $www_image_orig);
        cache($self);
    }
    return $self;
}

sub getBluecode {
    my ($self) = @_;

    return $self->{_bluecode};
}

sub setBluecode {
    my ($self, $bc) = @_;

    $self->{_bluecode} = $bc;
}

sub clear {
    my ( $self ) = @_;

    my $blue_code_file = $main::config->{BlueCode}->{'File'};
    my $priming_bluecode = $main::config->{BlueCode}->{'PrimingValue'};
    if ( -f $blue_code_file ) {
        unlink($blue_code_file) or die "Can't unlink $blue_code_file: $!\n";
    }
    $self->{_bluecode} = $priming_bluecode;
    return $self->{_bluecode};
}

sub save_is_blueist {
    my ( $self, $bf_50pct, $bf_orig ) = @_;
    my $bc = $self->{_bluecode};
    my $blueist_file_50pct = get_www_dir("", $main::mode) . $main::config->{BlueCode}->{'BlueistImage'} . "_50pct";
    my $blueist_file_orig = get_www_dir("", $main::mode) . $main::config->{BlueCode}->{'BlueistImage'} . "_orig";

    # local copies
    copy($bf_50pct, $blueist_file_50pct) or die "Can't copy $bf_50pct to $blueist_file_50pct: $!\n";
    copy($bf_orig, $blueist_file_orig) or die "Can't copy $bf_orig to $blueist_file_orig: $!\n";
    print "Bluecode copy: $bf_50pct to $blueist_file_50pct\n" if ( $main::debug );
    print "Bluecode copy: $bf_orig to $blueist_file_orig\n" if ( $main::debug );

    # copies on google
    my $bucket_dir = $main::config->{GStore}->{'BlueistDir'};
    $main::gstore->cp_fs2bucket($bf_50pct, $bucket_dir);
    $main::gstore->cp_fs2bucket($bf_orig, $bucket_dir);

}

sub cache {
    my ($self) = @_;

    my $blue_code_file = get_www_dir("", $main::mode) . $main::config->{BlueCode}->{'File'};
    open F, ">$blue_code_file" or die "Can't open $blue_code_file$!\n";
    print F $self->{_bluecode};
    print "writing bluecode file.  Current bluecode: ", $self->{_bluecode}, "\n" if ( $main::debug );
    close F;
}

sub prime {
    my ($self) = @_;

    my $priming_bluecode = $main::config->{BlueCode}->{'PrimingValue'};
    my $blue_code_file = $main::config->{BlueCode}->{'File'};

    if ( -f $blue_code_file ) {
        open F, $blue_code_file or die "Can't open $blue_code_file$!\n";
        my $in = <F>;
        chomp($in);
        $self->{_bluecode} = $in;
        print "Bluecode file ($blue_code_file) found, priming with $in\n" if ( $main::debug );
        return $self;
    }
    else {
        print "No bluecode file, priming with $priming_bluecode\n" if ( $main::debug );
        $self->{_bluecode} = $priming_bluecode;
        return $self;
    }
}

END {    # module clean-up code here (global destructor)
    ;
}

1;  # don't forget to return a true value from the file
