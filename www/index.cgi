#!/usr/bin/perl

use CGI;
my $q = CGI->new;

$fn = "/var/www/bib/camera/tl_url";
open F, $fn;
my $url = <F>;
close F;

my $title = 'SeaCrest 6 Webcam';
print header;
print $q->header(),
      $q->start_html($title), "\n",
      $q->h1({align=>center}, $title), "\n",
      $q->h3({align=>center}, 'Current Image'), "\n";
print "<center>\n";
print $q->img({align=>center, src=>'current_image_50pct.jpg'});
print $q->h3({align=>center}, 'Latest Time Lapse'), "\n";
print "<P>if unable to see movie use <a href=\"", $url, "\">this link</a></p>\n";
print $q->iframe({align=>left, id=>'ytplayer',type=>"text/html",width=>"640",height=>"390",src=>$url,frameborder=>"0",align=>'center'});
print "Updated hourly while the sun is up.<BR>\n";
print "</center>\n";
print $q->end_html;           
