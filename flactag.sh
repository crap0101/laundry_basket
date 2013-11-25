#!/bin/bash


function help () {
    echo "Print flac tags and others info
Require: awk, getopts, metaflac, paste, tr
Usage: $1 -[aAtTyscb] file [file ...]
    -h    show this help and exit
  By default print all available informations. To select
  one or more info use:
    -a    artist
    -A    album
    -d    duration
    -t    title
    -T    track number
    -y    year
    -s    sample rate
    -c    channels
    -b    bits per sample
"
}

function track_time () {
    metaflac --show-total-samples --show-sample-rate "$1" | tr '\n' ' ' | awk '
        {sec = $1/$2}
        END {
            min = sec/60
            sec %= 60
            printf "%02d:%02d", min, sec
        }'
}

function track_info () {
    metaflac --show-tag=Tracknumber --show-tag=Title --show-tag=Album --show-tag=Artist --show-tag=Year "$1"
    echo -e "SAMPLE_RATE\nCHANNELS\nBPS" | paste -d= - <( metaflac --show-sample-rate --show-channels --show-bps "$1" )
}

function format_info () {
    echo "$1"
    track_info "$1"
    echo "DURATION=$(track_time "$1")"
}

if [ $# -eq 0 ]
then
    help "$(basename "$0")"
    exit 0
fi

filter=
while getopts "aAdtTyscbh:" arg
do
    case $arg in
	a) filter+="ARTIST|";;
	A) filter+="ALBUM|";;
	d) filter+="DURATION|";;
	t) filter+="TITLE|";;
	T) filter+="TRACKNUMBER|";;
	y) filter+="YEAR|";;
	s) filter+="SAMPLE_RATE|";;
	c) filter+="CHANNELS|";;
	b) filter+="BPS|";;
        *|h)
            help "$(basename "$0")"
            exit 0
    esac
done
if [ -n "$filter" ]; then
    filter="^(${filter%|})"
fi

for track in "$@"; do
    format_info "$track" 2>/dev/null | grep -E "$filter"
    echo
done