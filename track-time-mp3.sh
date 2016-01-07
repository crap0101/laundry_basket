#!/bin/bash


if [ $# -eq 0 ]
then
    echo "Print the playing time of the provided mp3 files."
    echo "USAGE: `basename $0` file ..."
    echo "REQUIRES: mp3info, awk"
    exit 0
fi

mp3info -rm -p "%02m:%02s (%r Kb/s)\t%f\n" "$@" | awk '
    BEGIN {
        mins = 0;
        secs = 0;
    }
    $1 ~ /[0-9]+:[0-9]+/ {
        split($1, a, ":");
        mins += a[1]; secs += a[2]
    }
    { print }
    END {
        madd = secs/60;
        secs = secs%60;
        printf("Total time: %02d:%02d\n",  mins+madd, secs)
    }'
