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

$fn = $config->{'Video'}->{'Daily'}->{'URL_file'};
open F, $fn;
my $url = <F>;
close F;

my $title = 'Seacrest 6 Webcam';
#my $image = "./current_image_50pct.jpg";
my $image = "http://commondatastorage.googleapis.com/cam_bucket%2Fcurrent%2Fcurrent_image_50pct.jpg";
#my $full_image = "./current_image_orig.jpg";
my $full_image = "http://commondatastorage.googleapis.com/cam_bucket%2Fcurrent%2Fcurrent_image_orig.jpg";

my $force = 0;

my $mode = "prod";

my $dt = DateTime->now(  time_zone => $config->{'General'}->{'Timezone'} );
my $s = new SC6::Cam::Sun();
print "Now: $dt\n" if ( $debug );

my $image_title = "Current Image";
my $timeoutPeriod = '300000';
if ( ! $s->is_sun($dt, $debug) ) {
    my $bi = "http://commondatastorage.googleapis.com/cam_bucket%2Fcurrent%2Fblueist_image.jpg";
    $image = $bi;
    $full_image = $bi;
#    $image = "./" . $config->{BlueCode}->{Blueist_image};
#    $full_image = "./" . $config->{BlueCode}->{Blueist_image};
    $image_title = "Image from earlier";
    $timeoutPeriod = '1800000';
}

#print header;
#print "Content
#print "<HTML>\n";
#print "<head>\n";

print "Content-Type: text/html; charset=ISO-8859-1\n\n";
print "<!DOCTYPE html\n";
print "         PUBLIC \"-//W3C//DTD XHTML 1.0 Transitional//EN\"\n";
print "         \"http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd\">\n";
print "<html xmlns=\"http://www.w3.org/1999/xhtml\" lang=\"en-US\" xml:lang=\"en-US\">\n";
print "<TITLE>$title</TITLE>";
print "<script type=\"text/JavaScript\">\n";
print "<!--\n";
print "function timedRefresh(timeoutPeriod) {\n";
print "    setTimeout(\"location.reload(true);\",timeoutPeriod);\n";
print "}\n";
print "//   -->\n";
print "</script>\n";
print "<center>\n";
my $heredoc = <<END;
<script>
  (function(i,s,o,g,r,a,m){i['GoogleAnalyticsObject']=r;i[r]=i[r]||function(){
  (i[r].q=i[r].q||[]).push(arguments)},i[r].l=1*new Date();a=s.createElement(o),
  m=s.getElementsByTagName(o)[0];a.async=1;a.src=g;m.parentNode.insertBefore(a,m)
  })(window,document,'script','//www.google-analytics.com/analytics.js','ga');

  ga('create', 'UA-47293115-1', 'selby.com');
  ga('send', 'pageview');

</script>
END
print $heredoc; 
print "</head>\n";
print "<body onload=\"JavaScript:timedRefresh(", $timeoutPeriod, ");\">\n";



#print $q->header();
#print $q->start_html($title), "\n";
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
print "<BR>\n";
print "<P>\n";

print $q->h3("Weater Observations<BR>\n");
print $q->table({-border=>undef},
           $q->Tr({-align=>'CENTER',-valign=>'TOP'},
           [
	      $q->td(["<A HREF=\"http://www.wrh.noaa.gov/mesowest/getobext.php?wfo=sew&sid=AU711&num=48&raw=0&dbn=m\"><IMG height=\"50\" width=\"50\" src=\"./NWS_Logo.png\"/></A>",
                      "<A HREF=\"http://www.findu.com/cgi-bin/wxpage.cgi?call=K7SSW&last=12\"><IMG height=\"50\" width=\"50\" src=\"./cwp_logo.gif\"/></A>",
                      "<A HREF=\"http://www.sailflow.com/spot/116314\"><IMG height=\"50\" width=\"50\" src=\"./sf.png\"/></A>",
                     ]),
           ]
           )
        );

print "</center>\n";
print $q->end_html;           
