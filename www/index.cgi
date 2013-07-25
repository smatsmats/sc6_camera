#!/usr/bin/perl

use CGI;
use DateTime;
use SC6::Cam::General;
use SC6::Cam::Config;
use SC6::Cam::Sun;

my $q = CGI->new;

my $c = new SC6::Cam::Config();
our $config = $c->getConfig();
our $debug = 0;

$fn = "/var/www/bib/camera/tl_url";
open F, $fn;
my $url = <F>;
close F;

my $title = 'SeaCrest 6 Webcam';
my $image = "./current_image_50pct.jpg";

my $force = 0;

my $mode = "prod";

my $dt = DateTime->now(  time_zone => 'America/Los_Angeles' );
my $s = new SC6::Cam::Sun();
print "Now: $dt\n" if ( $debug );

if ( ! $s->is_sun($dt, $debug) ) {
    $image = "./" . $config->{BlueCode}->{Blueist_imag};
}

#print header;
print $q->header();
print $q->start_html($title), "\n";
print "<center>\n";
print $q->h1($title), "\n";
print $q->h3('Current Image'), "\n";
print $q->img({src=>$image});
print $q->h3('Latest Time Lapse'), "\n";
print "<P>if unable to see movie use <a href=\"", $url, "\">this link</a></p>\n";
print $q->iframe({align=>left, id=>'ytplayer',type=>"text/html",width=>"640",height=>"390",src=>$url,frameborder=>"0",align=>'center'});
print "Updated hourly while the sun is up.<BR>\n";
print "</center>\n";
print $q->end_html;           
