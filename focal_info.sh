#!/bin/bash
#
# author: Marco Chieppa | crap0101
#

REQUIRES="exiftran gawk printf sort pwd cut basename find xargs"
IMG_PLOT_DIMS=6000,2000

function help () {
    echo "Collect or print info about the mostly used focal lengths.
USAGE: $1 [OPTION [ARG]]
OPTIONS:
  -h         print this help
  -C         check for required programs
  -c PATH    retrive info from every jpg file in PATH (recursive)
  -p PATH    plot info from the file at PATH [*1]
  -s PATH    show info from the file at PATH [*2]
PLOT OPTIONS (must precedes -s, ignored otherwise):
  -d W,H     output image dimensions (default: $IMG_PLOT_DIMS).

[*1] Require gnuplot
[*1] PATH must be a file produced by a previous running with the -s option
[*2] PATH must be a file produced by a previous running with the -c option
All outputs goes to stdout, the -p option produce a jpg file.
Without options/arguments run the collecting job from the current directory.
Returns 0 on success or >0 on failure (maybe) ***XXX+TODO***.
Requires: (getopts) $REQUIRES
Optional: which (for -C) gnuplot (for -p)
" >&2
}

function check_dims () {
    if [[ ! $1 =~ ^[0-9]+,[0-9]+$ ]]; then
	return 1
    fi
    return 0
}

function check_requires () {
    local retcode=0
    for prog in $REQUIRES; do
	which $prog >/dev/null || { echo "missing: $prog" >&2; retcode=1; }
    done
    return $retcode
}

function collect () {
    find "$1" -type f -iregex '.*\.jpe?g' -print0 | xargs -0 exiftran -d \
	| awk -F ' {2,}' '
        function __print(model, focal_length) {
            print model,focal_length,focal_mult[model]*focal_length
        }
        BEGIN {
            OFMT = "%.0f"
            OFS = ";"
            focal_mult["DMC-GH3"] = 2
            focal_mult["E-P2"] = 2
            focal_mult["SP800UZ"] = 5.71
            focal_mult["Canon PowerShot A460"] = 7.03
            focal_mult["Canon PowerShot A620"] = 4.79
            focal_mult["Canon PowerShot A70"] = 6.48
            focal_mult["Canon PowerShot S110"] = 4.62
            _undef_model = _model = "???"
            _undef_focal_length = _focal_length = "???"
        }
        $1 == "--" {
            __print(_model, _focal_length)
            _model = _undef_model
            _focal_length = _undef_focal_length
        }
        $2 == "0x0110" {
            _model = $4
        }
        $2 == "0x920a" {
            _focal_length = sprintf("%.2f", $4)
        }'
}

function plot () {
awk -F: '
    function getfn(str) {
        return int(gensub(/^([0-9]+).*/, "\\1", 1, str))
    }
    function frange(strange) {
        split(strange, farr, "-")
    }
    BEGIN {
        PROCINFO["sorted_in"] = "@ind_num_asc"
    }
    getfn($1) < 23 { arr["0-23"] += $2; next }
    getfn($1) < 36 { arr["24-35"] += $2; next }
    getfn($1) < 51 { arr["36-50"] += $2; next }
    getfn($1) < 86 { arr["51-85"] += $2; next }
    getfn($1) < 106 { arr["86-105"] += $2; next }
    getfn($1) < 201 { arr["106-200"] += $2; next }
    getfn($1) < 401 { arr["201-400"] += $2; next }
    { arr["401-10000"] += $2 }
    END {
        for (f in arr) {
            frange(f)
            printf("%s:%d:%d:%d\n", f, arr[f], farr[1], farr[2])
        }
    }
' "$1" | gnuplot -e "
set xlabel 'focal';
set ylabel 'shots';
set terminal jpeg size $IMG_PLOT_DIMS;
set datafile separator ':';
set style fill solid;
set ytic nomirror;
set xtic nomirror in rotate by 90;
set xtics center offset 0,-1;
set autoscale;
unset key;
plot '$1' using 1:2:xticlabels(1) with linespoints, \
     '$1' using 1:2:2 with labels, \
     '-' using ((\$4+\$3)/2):2:(sprintf(\"(%d-%d)\", \$3, \$4)) \
        with labels center point pt 7;
"
}

function show () {
    cut -d ';' -f3 "$1" | awk '
        BEGIN {
            PROCINFO["sorted_in"] = "@ind_num_asc"
        }
        {arr[$1] += 1}
        END {
            for (f in arr)
                printf "%smm: %d\n", f, arr[f]
        }'
}

if [ $# -lt 1 ]; then
    collect "$(pwd)"
    exit $?
fi

while getopts ":Cc:d:p:s:h" arg
do
    case $arg in
	C)
	    check_requires
	    exit $?;;
	c)
	    collect "$OPTARG"
	    exit $?;;
	d)
	    if check_dims "$OPTARG"; then
		IMG_PLOT_DIMS="$OPTARG"
	    else
		echo "Invalid dimension: $OPTARG" >&2
		exit 1
	    fi;;
	p)
	    plot "$OPTARG"
	    exit $?;;
	s)
	    show "$OPTARG"
	    exit $?;;
	\?)
	    echo "Invalid option: -$OPTARG" >&2
	    exit 1;;	
	:)
	    echo "Option -$OPTARG requires an argument." >&2
	    exit 1;;
        *|h)
            help "$(basename "$0")"
            exit 1;;
    esac
done

exit $?
