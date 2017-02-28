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
    my $self = {
        _mode => shift,
        _dryrun => shift,
    };

    prime($self);

    bless $self, $class;
    return $self;
}

sub checkBluecode {
    my ($self, $new_image) = @_;

    my $new_bluecode = $new_image->getBluecode();
    my $current_bluecode = $self->getConfirmedBluecode();

    if ( $new_bluecode > $current_bluecode ) {
        print "new bluecode: $new_bluecode old: ", $self->{_bluecode}, "\n";
        my $www_image_50pct = $new_image->{_www_image_50pct};
        my $www_image_orig = $new_image->{_www_image_orig};
        $self->{_bluecode} = $new_bluecode;
        save_is_blueist_stash($self, $new_image);
        save_is_blueist_local($self, $www_image_50pct, $www_image_orig);
        cache($self);
        return 1;
    }
    return 0;
}

sub getConfirmedBluecode {
    my ($self) = @_;
    my $blue_code_file = $main::config->{BlueCode}->{'File'};

    my $new_file_time = (stat($blue_code_file))[9];
    if ( $new_file_time != $self->{_blue_change_time} ) {
        if ( -f $blue_code_file ) {
            $self->{_bluecode} = readBluecodeFile($blue_code_file);
            $self->{_blue_change_time} = (stat($blue_code_file))[9];
        }
    }
    return $self->{_bluecode};
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
    $self->{_blue_change_time} = 0;
    return $self->{_bluecode};
}

sub save_is_blueist_stash {
    my ( $self, $new_image ) = @_;

    my $stash_dir = get_image_dir($new_image->{_dt}, "stash", $main::mode);
    my $stash = $stash_dir . "/" . $self->{_bluecode} . ".jpg";
    my $image = $new_image->{_output};
    print "going to symlink $image to $stash\n";
    symlink($image, $stash) or die "Can't symlink $image to $stash: $!\n";
}

sub save_is_blueist_local {
    my ( $self, $bf_50pct, $bf_orig ) = @_;
    my $bc = $self->{_bluecode};
    my $blueist_file_50pct = get_www_dir("", $main::mode) . $main::config->{BlueCode}->{'BlueistImage'} . "_50pct";
    my $blueist_file_orig = get_www_dir("", $main::mode) . $main::config->{BlueCode}->{'BlueistImage'} . "_orig";

    # local copies
    copy($bf_50pct, $blueist_file_50pct) or die "Can't copy $bf_50pct to $blueist_file_50pct: $!\n";
    copy($bf_orig, $blueist_file_orig) or die "Can't copy $bf_orig to $blueist_file_orig: $!\n";
    print "Bluecode copy: $bf_50pct to $blueist_file_50pct\n" if ( $main::debug );
    print "Bluecode copy: $bf_orig to $blueist_file_orig\n" if ( $main::debug );

}

sub cache {
    my ($self) = @_;

    my $blue_code_file = get_www_dir("", $main::mode) . $main::config->{BlueCode}->{'File'};
    open F, ">$blue_code_file" or die "Can't open $blue_code_file$!\n";
    print F $self->{_bluecode};
    print "writing bluecode file locally.  Current bluecode: ", $self->{_bluecode}, "\n" if ( $main::debug );
    $self->{_blue_change_time} = (stat($blue_code_file))[9];
    close F;
}

sub prime {
    my ($self) = @_;

    my $priming_bluecode = $main::config->{BlueCode}->{'PrimingValue'};
    my $blue_code_file = get_www_dir("", $main::mode) . $main::config->{BlueCode}->{'File'};

    if ( -f $blue_code_file ) {
        $self->{_bluecode} = readBluecodeFile($blue_code_file);
        print "Bluecode file ($blue_code_file) found, priming with ", $self->{_bluecode}, "\n" if ( $main::debug );
        return $self;
    }
    else {
        print "No bluecode file, priming with $priming_bluecode\n" if ( $main::debug );
        $self->{_bluecode} = $priming_bluecode;
        return $self;
    }
}

sub readBluecodeFile {
    my $file = shift;
    open F, $file or die "Can't open $file $!\n";
    my $in = <F>;
    chomp($in);
    return $in;
}

END {    # module clean-up code here (global destructor)
    ;
}

1;  # don't forget to return a true value from the file
