#!/usr/bin/perl

use CGI;
use DateTime;
use SC6::Cam::General;
use SC6::Cam::Config;
use SC6::Cam::Sun;

my $q = CGI->new;

my $c = new SC6::Cam::Config("/usr/local/cam/conf/config.yml");
our $config = $c->getConfig();
our $debug = 0;

$fn = "/var/www/bib/camera/tl_url";
open F, $fn;
my $url = <F>;
close F;

my $title = 'Seacrest 6 Webcam';
my $image = "./current_image_50pct.jpg";
my $full_image = "./current_image_orig.jpg";

my $force = 0;

my $mode = "prod";

my $dt = DateTime->now(  time_zone => $config->{'General'}->{'Timezone'} );
my $s = new SC6::Cam::Sun();
print "Now: $dt\n" if ( $debug );

my $image_title = "Current Image";
if ( ! $s->is_sun($dt, $debug) ) {
    $image = "./" . $config->{BlueCode}->{Blueist_image};
    $full_image = "./" . $config->{BlueCode}->{Blueist_image};
    $image_title = "Image from earlier";
}

my $timoutPeriod = '300';
#print header;
#print "Content
#print "<HTML>\n";
#print "<head>\n";
#print "<script type=\"text/JavaScript\">\n";
#print "<!--\n";
#print "function timedRefresh($timeoutPeriod) {\n";
#print "    setTimeout(\"location.reload(true);\",timeoutPeriod);\n";
#print "}\n";
#print "//   -->\n";
#print "</script>\n";
#print "<TITLE>$title</TITLE>";
#print "</head>\n";
#print "<body onload=\"JavaScript:timedRefresh(5000);\">\n";

print $q->header(-refresh=>'300');
print $q->start_html($title), "\n";
print "<center>\n";
print $q->h1($title), "\n";
print $q->h3($image_title), "\n";
print "<A HREF=\"", $full_image, "\"><img src=\"", $image, "\"/></A>\n";
#print $q->img({src=>$image});
print $q->h3('Latest Time Lapse'), "\n";
print "<P>if unable to see movie use <a href=\"", $url, "\">this link</a></p>\n";
#print $q->iframe({align=>left, id=>'ytplayer',type=>"text/html",width=>"640",height=>"390",src=>$url,frameborder=>"0",align=>'center'});
print "<iframe width=\"640\" height=\"390\" src=\"", $url, "\" frameborder=\"0\" allowfullscreen></iframe>\n";
print "<BR>\n";
print "Movie is updated hourly while the sun is up.<BR>\n";
print "Movie is unavailable while being updated, someday I'll fix that.<BR>\n";
print "Don't know why fullscreen doesn't work, use the link above if you'd like a bigger movie.<BR>\n";
print scalar localtime(), "\n";
print "Page should refresh every 5minutes\n";
print "</center>\n";
print $q->end_html;           
