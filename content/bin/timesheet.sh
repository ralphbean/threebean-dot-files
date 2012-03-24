#!/bin/bash

source /home/threebean/.bashrc

phrase="1-weeks-ago"
fmt="%m/%d/%Y"
start=$(date +$fmt -d $phrase)
end=$(date +$fmt)
filter="project.isnt:family project.isnt:xmas project.isnt:cersc project.isnt:iso project.isnt:monroe project.isnt:house project.isnt:misc project.isnt:rit project.isnt:tos-rit-projects-seminar project.isnt:music project.isnt:hfoss"

echo "    (generated at $(date))"
echo
echo " -- Tasks completed from $start to $end (back $phrase) -- "
/usr/local/bin/task work_report $filter end.after:$start

echo
echo 
echo " -- Upcoming tasks -- "
/usr/local/bin/task next $filter

echo
echo
echo " -- Summary -- "
/usr/local/bin/task summary $filter

echo
echo
echo " -- History -- "
/usr/local/bin/task history $filter
/usr/local/bin/task ghistory $filter
/usr/local/bin/task burndown.daily
/usr/local/bin/task burndown
