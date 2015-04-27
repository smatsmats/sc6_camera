#!/usr/bin/perl

my $src = "/usr/local/cam/data/cam_images/20130913/orig/";
my $linkdir = "/tmp/link_dir/";

opendir DIR, $src;
my @d_list = readdir(DIR);
closedir DIR;

if ( -d $linkdir ) {
    print `rm -r $linkdir`;
}

mkdir ($linkdir, 0775) or die "can't make dir $linkdir: $!\n";

my $c = 1;
foreach my $f ( sort @d_list ) {
    next if ( $f eq "." or $f eq "..");
    my $ff = $src . $f;
    print $ff, "\t";
    my $lf = sprintf ("%s/%05d.jpg", $linkdir, $c);
    print $lf, "\n";
    link $ff, $lf or die "Can't link  $ff, $lf\n";
    $c++;
}
