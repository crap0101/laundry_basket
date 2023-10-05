#!/bin/bash

function usage ()
{
    echo -ne "$0: remove backup file by suffix.
    USAGE: $0 [[-s SUFFIX] ...] [PATH ...]
    OPTIONS:
        -d DEPTH    Descend at most levels of directories
        -s SUFFIX   remove files ending in SUFFIX, (a find's findutils
                    -regex pattern, See \"man 1 find\" for details).
                    Default to \".*~$\".
        -v          verbose. Print removed files.
        -h          print this help and exit
    If no PATH are provided, uses the current directory.
"
}

set -o noglob
shopt -u nullglob

SFX=( )
SFX_DEFAULT=( '-regex ".*~$" -o' )
DEPTH=""
VERBOSE=""
ERRORS=( )

while getopts "d:s:vh" arg
do
    case $arg in
    d)
        if [ "$OPTARG" -le 0 ]; then
        echo "option -$arg: invalid argument <$OPTARG>"
        exit 1
        fi
        DEPTH="-maxdepth $OPTARG";;
	s)
	    SFX[${#SFX[@]}]="-regex $OPTARG -o";;
    v)
        VERBOSE="-print";;
    *|h)
        usage
        exit 1;;
    esac
done
shift $((OPTIND-1))

if [ ${#SFX[@]} -eq 0 ]; then
    SFX="${SFX_DEFAULT[@]}"
fi
SFX[${#SFX[@]}]="-false"

err_out_file=$(mktemp)
if [ "$?" -ne 0 ]; then
    echo "***can't create tempfile, errors on /dev/null"
    err_out_file=/dev/null
fi

OLD_IFS=${IFS}
IFS=""
if [ $# -lt 1 ]; then
    paths=( . );
else
    paths=( $@ );
fi

for path in "${paths[@]}"; do
    # ${SFX[@]} too complex for expansion :-|
    # ----------↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓---- shit
    eval find "$(printf \"\"%q\"\" ${path})" $DEPTH "-type f" "\( ${SFX[@]} \)" -delete "$VERBOSE" 2>$err_out_file
    exit_status=$?
    if [ "$exit_status" -ne 0 ]; then
    ERRORS[${#ERRORS[@]}]=$exit_status
    fi
done
IFS=${OLD_IFS}

if [ ${#ERRORS[@]} -gt 0 ]; then
    echo -n "*** some errors occured, find's exits status are:"
    for err in ${ERRORS[@]}; do
        echo -n "$err "
    done
    echo ""
    if [ $err_out_file != "/dev/null" ]; then
        echo "***see errors in $err_out_file"
    fi
else
    rm "$err_out_file"
fi
