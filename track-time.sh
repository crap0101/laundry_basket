#!/bin/bash


if [ $# -eq 0 ]
then
    echo "Print the playing time of the provided media files."
    echo "USAGE: `basename $0` file ..."
    echo "REQUIRES: mediainfo, gawk >= 4"
    exit 0
fi

for arg in "$@"
do
    duration="$(mediainfo "$arg" | grep -m1 ^Dur)"
    printf "%s\t$(basename "$arg")\n" "$duration" 
done | gawk '
    BEGIN {
        secs = 0
        mins = 0
    }
    {
        if  (match($0, /([0-9]+)mn\s+([0-9]+)s\t(.*)$/, arr) != 0) {
            mins += arr[1]
            secs += arr[2]
            printf ("%02d:%02d\t%s\n", arr[1], arr[2], arr[3])
        } else if (match($0, /([0-9]+)s\t(.*)$/, arr) != 0) {
            secs += arr[1]
            printf ("00:%02d\t%s\n",  arr[1], arr[2])
        } else
            print "ERROR: Malformed time: " $0
    }
    END {
        mins += secs/60
        secs = secs%60
        printf "Total Time: %02d:%02d\n", mins, secs
    }'
