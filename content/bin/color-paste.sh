#!/bin/bash
# Script to take the output of commands and post them to a tmp web directory
# for easy sharing.  Requires python-ansi2html.
#
# Author: Ralph Bean <rbean@redhat.com>
# License: GPLv3+

# Edit the following three variables to suit your needs
WEB_USER=threebean
WEB_HOST=threebean.org
WEB_DIR=~/webapps/static

echo "Creating file"
outfile=$(mktemp --suffix=.html)
ansi2html < /dev/stdin > $outfile
chmod o+r $outfile

echo "Uploading $outfile"
scp $outfile $WEB_USER@$WEB_HOST:$WEB_DIR$outfile

echo "Removing $outfile"
rm $outfile

echo
echo http://$WEB_HOST$outfile
