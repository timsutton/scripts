#!/bin/sh

ac -p | sort -nrk 2 | awk 'NR >= NF {print $1; exit}'
