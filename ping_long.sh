#!/bin/bash


function usage () {
    cat <<HELP
DESCRIPTION: run ping again and again, saving statistical informations.
SYNOPSIS: $(basename "$0") -h|COMMAND [OPTIONS]
    COMMAND can be:
        start    Start pinging.
	stop     Stop pinging.
        stat     Show statistical informations.
    OTHER OPTIONS:
        -h         show this help and exit.
OPTIONAL:
    For runtime info: https://github.com/crap0101/laundry_basket/blob/master/secs2time.sh
HELP
}

DATAFILE=/tmp/ping_long.data
LOCKFILE=/tmp/ping_long.lock


function start () {
    if [ -a "$LOCKFILE" ]; then
	echo "$0 already running!"
	echo "checking for process id..."
	if ps -hp "$(cat $LOCKFILE)"; then
	    echo "found that... kill it if you like, then restart."
	else
	    echo "No meaningful pid found. (You) Try deleting manually '$LOCKFILE'"
	fi
	return 1
    else
	echo -n "$$" > "$LOCKFILE"
	return $?  # in case of error creating the lockfile
    fi
}


function stop () {
    if [ -a "$LOCKFILE" ]; then
	if ps -hp "$(cat $LOCKFILE)"; then
	    pid="$(cat $LOCKFILE)"
	    if kill $pid; then
		rm "$LOCKFILE"
		return $?
	    else
		echo "Can't kill pid '$pid', leaving intact '$LOCKFILE'"
		return 1
	    fi
	else
	    ps -p "$(cat $LOCKFILE)"
	    echo "Can't find program's pid, leaving intact '$LOCKFILE'"
	    return 1
	fi
    else
	echo "(Maybe) Not running."
	echo "Can't find lockfile '$LOCKFILE', trying searching for command name..."
	if ps h -C "$0"; then
	    echo "Found that."
	else
	    echo "No meaningful pid found."
	fi
	return 1
    fi
}


function getstat () {
    retcode=0
    if ! [ -a "$DATAFILE" ]; then
	echo "No data file found at '$DATAFILE'"
	return 1
    fi
    succeed=$(cat "$DATAFILE" | tr -dc 1 | wc -c)   # succeed runs
    (( retcode += $? ))
    failed=$(cat "$DATAFILE" | tr -dc 0 | wc -c)   # failed runs
    (( retcode += $? ))
    total=$(( succeed + failed ))
    (( retcode += $? ))
    start_time=$(stat -c %w $LOCKFILE 2>/dev/null)
    if ! [ "$start_time" ]; then start_time="NOT RUNNING, NOT AVAILABLE"; fi
    if [ "$(tail -c 1 $DATAFILE)" == "1" ]; then
	last="Succeed"
    else
	last="Failed"
    fi
    cat <<STAT_INFO
Start Time:                  $start_time
First Data registering Time: $(stat -c %w $DATAFILE)
Current Time:                $(date '+%F %T')$(runtime_info)
Total runs: ${total}
Succeed: $succeed ($(( succeed * 100 / total ))%)
Failed: $failed ($(( failed * 100 / total ))%)
Last: $last
STAT_INFO
    (( retcode += $? ))
    return $retcode
}


function runtime_info () {
    which secs2time.sh &>/dev/null
    if [ $? -ne 0 ]; then
	echo -n ""
    else
	echo -ne "\nRuntime: $(secs2time.sh $(( $(date +%s) - $(stat -c %W $DATAFILE) )))\n"
    fi
}

function _fakerun () {
    > "$DATAFILE"
    for i in $(seq 10000); do
	if (( $i % 3 )); then
	   echo -n 1 >> "$DATAFILE"
	else
	    echo -n 0 >> "$DATAFILE"
	fi
	sleep 1
    done
}

function run () {
    timeout=10
    sleeptime=60
    rm "$DATAFILE"
    while true; do
	st=$(date +%s)
	if ping -c 1 -W $timeout google.it; then
	    echo -n 1 >> "$DATAFILE"
	else
	    echo -n 0 >> "$DATAFILE"
	fi
	sleep $((sleeptime - ($(date +%s) - st) ))
	#&>/dev/null
    done
}


if [ $# -eq 0 ]
then
    usage $0
    exit 1
fi

case "$1" in
    "start")
	echo "start pinging..."
	if start; then
	    if ! run; then
		echo "Mmm... there's an error..."
		exit 1
	    fi
	fi
	exit $?
        ;;
    "stop")
	echo "stop pinging..."
	stop
	exit $?
	;;
    "stat")
	if ! getstat; then
	    retcode=$?
	    echo "Some errors computing stats..."
	    exit $retcode
	fi
	exit 0
	;;
    *|h)
	usage $0
        exit 0
esac

exit 99 # not really

# ...maybe later:
shift 1

for arg in "$@"
do
    : #echo "arg:$arg"
done
