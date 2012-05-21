#!/bin/bash

# dircheck_hash v.0.7
# find differences between two directories

# Copyright (C) 2010  Marco Chieppa (aka crap0101)

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to
# deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
# sell copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

# THIS SOFTWARE IS PROVIDED BY THE AUTHOR ``AS IS'' AND ANY EXPRESS OR
# IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.
# IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS;
# OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
# WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR
# OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF
# ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

function usage ()
{
    echo -ne "dircheck_hash: compare files by names between dirs.
    USAGE: $0 [-n] [-m MAXDEPTH] [-c HASHPROG] -f DIR1 [-s DIR2]
    OPTIONS:
        -h       print this help and exit
        -v       print program's version and exit
        -n       Do not count files
        -m NUM   Descend at most NUM (a  non-negative  integer) levels  of
                 directories. -maxdepth 0 means  only  apply  the  tests and
                 actions to the command line arguments
        -c EXE   program to use for file comparison (default md5sum)

        -f PATH  First directory to compare (default to the current dir)
        -s PATH  Other directory to compare (default to the current dir)\n"
}

if [ $# -lt 1 ]; then
    usage
    exit 1
fi

_VERSION=0.7

MAXDEPTH=32767
IS_COUNT=1
TOTAL="-"
DIR1=$PWD
DIR2=$PWD
EXT_ERR=0
HASHPROG=md5sum

while getopts "hvnm:c:f:s:" arg
do
    case $arg in
        c)  HASHPROG=$OPTARG
            ;;
        m)
            MAXDEPTH=$OPTARG
            if [ $MAXDEPTH -lt 0 ]; then
                usage
                exit 255
            fi
            ;;
        n)
            IS_COUNT=0
            ;;
        f)
            DIR1=${OPTARG%/}
            ;;
        s)
            DIR2=${OPTARG%/}
            ;;
        v)
            echo $_VERSION
            exit 0
            ;;
        *|h)
            usage
            exit 1
    esac
done


if [ $IS_COUNT -eq 1 ]; then
    TOTAL=`find "$DIR1" -maxdepth $MAXDEPTH -type f | wc -l`
fi


function dcheck
{
    errors=0
    count=0
    skipped=0
    DIR1=$1
    DIR2=$2
    MAXDEPTH=$3
    TOTAL=$4
    HASHPROG=$5
    IFS=$'\n';
    for file in `find "$DIR1" -maxdepth $MAXDEPTH -type f`
    do
        (( count++ ))
        hashfile1=`$HASHPROG "$file" | awk '{print $1}'`
        append=${file:${#DIR1}}
        if [ ! -e "$DIR2/$append" ]
        then
	    echo -e "\n(not found, skipped) $DIR2/$append"
            (( skipped++ ))
        else
            hashfile2=`$HASHPROG "$DIR2/$append" | awk '{print $1}'`
            if [ "$hashfile1" != "$hashfile2" ]
            then
                (( errors++ ))
                echo -e "\nhash mismatch: $file\t$DIR2/$append"
            fi
        fi
        _i="\rchecking file $count/$TOTAL\tErrors:$errors\tSkipped:$skipped"
        echo -ne "$_i"

    done
    if [ $skipped -ne 0 ]; then
        EXT_ERR=1
    fi
    if [ $errors -ne 0 ]; then
       EXT_ERR=2
    fi
    echo
}



echo "checksum for files in $DIR1 against files in $DIR2"
dcheck "$DIR1" "$DIR2" $MAXDEPTH $TOTAL $HASHPROG

exit $EXT_ERR
