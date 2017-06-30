#!/usr/bin/perl

use DateTime;
use SC6::Cam::General;
use SC6::Cam::Config;
use SC6::Cam::Sun;
use Getopt::Long;
use Data::Dumper;

my $force = 0;
my $mode = "prod";

my $c = new SC6::Cam::Config("/usr/local/cam/conf/config.yml", $mode);
our $config = $c->getConfig();
our $debug = $c->getDebug();

$result = GetOptions (  "length=i" => \$length,    # numeric
                        "f|force"  => \$force,     # flag
                        "h|help"  => \$usage,      # function
			"d|debug"  => \$debug);    # flag

my $dt = DateTime->now(  time_zone => $config->{'General'}->{'Timezone'} );
my $s = new SC6::Cam::Sun();
print "Now: $dt\n" if ( $debug );
if ( $force ) {
    print "We're forced to do this\n" if ( $debug );
}
else {
    if ( $s->is_sun($dt) ) { 
        print "Sun is up!\n";
    }
    elsif ( $s->is_hour_after_dusk($dt) ) {
        print "Sun is down, but for less than an hour!\n";
    }
    else  {
        print "Sun is down!\n";
    }
}

print $s->sun_message();
print "We'll start the party at ", $s->start_time()->datetime, " (", $s->start_time()->epoch(), ")\n";
print "We'll close shop ", $s->end_time()->datetime, " (", $s->end_time()->epoch(), ")\n";
print "is_sun: ", $s->is_sun($dt), "\n";
print "is_after_sunrise: ", $s->is_after_sunrise($dt), "\n";
print "is_after_noon: ", $s->is_after_noon($dt), "\n";
print "is_after_sunset: ", $s->is_after_sunset($dt), "\n";
print "is_hour_after_dusk: ", $s->is_hour_after_dusk($dt), "\n";

exit;

