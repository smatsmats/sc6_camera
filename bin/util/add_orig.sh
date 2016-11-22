#!/bin/sh

for i in *; do name=`basename -s .jpg $i`; echo $name ; new=${name}_orig.jpg; echo $new ;  echo $i ; mv $i $new ;  done
