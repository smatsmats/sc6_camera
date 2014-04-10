#!/bin/sh

gsutil cp /var/www/bib/camera/current_image_orig.jpg gs://cam_bucket
gsutil cp /var/www/bib/camera/current_image_50pct.jpg gs://cam_bucket

