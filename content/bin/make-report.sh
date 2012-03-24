#!/bin/bash

today=$(date +%Y-%m-%d)
/home/threebean/bin/timesheet.sh | ansi2html | /home/threebean/bin/linkify.py > /tmp/timesheet.html
scp /tmp/timesheet.html threebean@threebean:~/webapps/static/timesheets/$today.html
scp /tmp/timesheet.html threebean@threebean:~/webapps/static/timesheets/latest.html
rm /tmp/timesheet.html
