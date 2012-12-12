#!/bin/bash
pushd /home/threebean/.task/
git commit -a -m 'Auto commit (cron)'
git push origin master
popd
