#!/bin/sh

ac -p | sort -nrk 2 | awk 'NR == 2 { print $1 }'
