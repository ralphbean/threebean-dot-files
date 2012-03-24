#!/usr/bin/env python
# linkify.py - Turns URLs into links.
#
# Using on a file:
#
#   $ linkify.py <filename>
#   <a href="http://lewk.org">http://lewk.org</a>
#
# Using within a pipeline:
#
#   $ echo 'http://lewk.org' | linkify.py
#   <a href="http://lewk.org">http://lewk.org</a>
#
# Author: Luke Macken <lmacken@redhat.com>
# License: GPLv3

import re, fileinput

regex = re.compile(r'https?:\/\/\S+')

for line in fileinput.input():
    for match in regex.findall(line):
        line = line.replace(match, '<a href="%s">%s</a>' % (match, match))
    print line,
