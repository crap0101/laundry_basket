#!/bin/bash

# dircheck_hash v.0.8
# find differences between two directories by file names

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
    echo -ne "dircheck_hash: compare files by names between dirs by file names.
    (version: $VERSION)
    USAGE: $0 [-n] [-m maxdepth] [-c hash_prog] [-i] dir1 dir2
    DESCRIPTION;
        Each FILENAME in the first directory will be compared against FILENAME
        in the second directory (if any).
    POSITIONAL ARGUMENTS:
        dir1     1st dir to compare
        dir2     2nd dir to compare
    OPTIONS:
        -c EXE   program to use for file comparison (default md5sum)
        -h       print this help and exit
        -i       swap directories comparison order (dir1 dir2 become dir2 dir1)
        -m NUM   Descend at most NUM (a  non-negative  integer) levels  of
                 directories. -m 0 means  only  apply  the  tests and
                 actions to the command line arguments
        -n       Do not count files
        -v       print program's version and exit\n"
}

if [ $# -lt 1 ]; then
    usage
    exit 1
fi

VERSION=0.8
max_depth=32000
must_count=1
total="-"
ext_err=0
hash_prog=md5sum
swap_dirs=0
dir1=
dir2=

while getopts "c:him:nv" opt
do
    case $opt in
        c)  hash_prog=$OPTARG
            ;;
        i)  swap_dirs=1
            ;;
        m)
            max_depth=$OPTARG
            if [ $max_depth -lt 0 ]; then
                usage
                exit 255
            fi
            ;;
        n)
            must_count=0
            ;;
        v)
            echo $VERSION
            exit 0
            ;;
        *|h)
            usage
            exit 1
    esac
done

shift $(($OPTIND - 1))
if [ $# -eq 0 ]; then
    usage
    exit 1
fi

for i in 1st 2nd; do
    if [ $# -gt 0 ]; then
        if [ -z "$dir1" ]; then 
            dir1="$1"
        elif [ -z "$dir2" ]; then
            dir2="$1"
        fi
        shift
    fi
done

#if [[ $# -gt 0 && -n "$dir1" && -n "$dir2" ]]; then
#    echo "Error: Unknown extra arguments ($#)"
#    exit 1
#fi
if [ -z "$dir1" -o -z "$dir2" ]; then
    echo "Error: not enough arguments!"
    exit 1
fi
if [ $# -gt 0 ]; then
    echo "Error: Unknown extra arguments ($#)"
    exit 1
fi

if [ $swap_dirs -eq 1 ]; then
    tmp="$dir1"
    dir1="$dir2"
    dir2="$tmp"
fi


function dcheck ()
{
    count=0
    errors=0
    skipped=0
    dir1="$1"
    dir2="$2"
    max_depth=$3
    hash_prog=$4
    if [ $5 -eq 1 ]; then
        total=$(find "$dir1" -maxdepth $max_depth -type f | wc -l)
    else
        total="-"
    fi
    find "$dir1" -maxdepth $max_depth -type f | while read file
    do
        (( count++ ))
        hashfile1=$($hash_prog "$file" | awk '{print $1}')
        append=${file:${#dir1}}
        if [ ! -e "$dir2/$append" ]; then
	        echo -e "\nm: $dir2/$append"
            (( skipped++ ))
        else
            hashfile2=$($hash_prog "$dir2/$append" | awk '{print $1}')
            if [ $hashfile1 != $hashfile2 ]; then
                (( errors++ ))
                echo -e "\nh: $file\t$dir2/$append"
            fi
        fi
        _i="\ri: checking file $count/$total\tErrors:$errors\tSkipped:$skipped"
        echo -ne "$_i"
    done
    echo
    if [ $skipped -ne 0 -o $errors -ne 0 ]; then
        return 1
    else
        return 0
    fi
}

echo "i: checksum for files in $dir1 against files in $dir2"
dcheck "$dir1" "$dir2" $max_depth $hash_prog $must_count
exit $?
