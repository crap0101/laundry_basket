#!/bin/bash
#
# author: Marco Chieppa | crap0101
#

function usage () {
    cat <<HELP
DESCRIPTION: track mouse position using xinput
SYNOPSIS: $(basename "$0") [OPTION]...
    -c         continuous tracking
    -d         show positions delta between two mouse (left) click events
    -s VALUE   sleep amount (in seconds) between queries (default: $sleep_time)
    -h         show this help and exit.
HELP
}

continuous=0
show_delta=0
sleep_time=0.07

while getopts "cds:h" arg
do
    case $arg in
	c)  continuous=1
	    ;;
	d)  show_delta=1
	    ;;
        s)  sleep_time="$OPTARG"
            ;;
        *|h)
	    usage $0
            exit 0
    esac
done
shift $(($OPTIND - 1))

trap "exit 0" SIGINT

mouse_id="$(xinput --list | sed -rn 's/.*mouse.*id=([0-9]+).*/\1/ip')"
xprev=-1
yprev=-1

while true
do
    button1state="$(xinput --query-state $mouse_id | sed -rn 's/.*button\[1\]=(\w+).*/\1/p')"
    if [ 1 -eq $continuous ] || [ "$button1state" = "down" ]; then
	xpos="$(xinput --query-state $mouse_id | sed -rn 's/.*valuator\[0\]=([0-9]+).*/\1/p')"
	ypos="$(xinput --query-state $mouse_id | sed -rn 's/.*valuator\[1\]=([0-9]+).*/\1/p')"
	if [ 0 -eq $show_delta ] || [ $xprev -lt 0 ] || [ $yprev -lt 0 ]; then
	    msg="mouse click at $xpos,$ypos"
	else
	    msg="mouse click at $xpos,$ypos (delta: $((xpos - xprev)),$((ypos - yprev)))"
	fi
	if [ 0 -eq $continuous ] || ([ $xpos -ne $xprev ] || [ $ypos -ne $yprev ]); then
	    echo $msg
	fi
	xprev=$xpos
	yprev=$ypos
    fi
    sleep $sleep_time
done

exit 0

# for comparison test:
while true
do
    pos="$(xdotool getmouselocation)"
    echo -ne "\r$pos"
    sleep 0.05
done
