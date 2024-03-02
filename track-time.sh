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
    duration=$(mediainfo --Inform="Audio;%Duration%" "$arg")
    printf "%s\t$(basename "$arg")\n" "$duration"
done | gawk '
    BEGIN {
        secs = 0
        mins = 0
    }
    $1 ~ /[0-9]+/ {
	s = $1 / 1000
        mins += track_m = s / 60
        secs += track_s = s % 60
	$1 = ""
	printf("%02d:%02d\t%s\n", track_m, track_s, $0)
	next
    }
    {
        printf("ERROR: Malformed time: <%s>\n", $1)
    }
    END {
        mins += secs/60
        secs = secs%60
        printf("Total Time: %02d:%02d\n", mins, secs)
    }'
