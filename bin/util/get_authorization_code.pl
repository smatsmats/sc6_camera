#!/usr/bin/perl

use strict;

my $oauth_url = "https://accounts.google.com/o/oauth2/auth";
my $scope = "email%20profile";
my $state = "state";
my $redirect_uri = "urn:ietf:wg:oauth:2.0:oob";
my $response_type = "code"; 
my $client_id = <client_id>
my $access_type = "offline"; 



my $url = $oauth_url . "?" . 
          "scope=" . $scope . "&" . 
	  "state=" . $state . "&" . 
	  "redirect_uri=" . $redirect_uri . "&" . 
	  "response_type=" . $response_type . "&" . 
	  "client_id=" . $client_id . "&" .
	  "access_type=" . $access_type;

my $cmd = "w3m '$url'";
print $cmd, "\n";

print "w3m -post post_file https://www.googleapis.com/oauth2/v3/token\n"
