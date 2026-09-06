#!/bin/bash
#
# author: Marco Chieppa | crap0101
#

# formatting options
_size="A4"
_margin="15mm"
_column_gap="15mm"
_font_family="sans-serif"
_line_height="1.4"
_font_size="10pt"

# other options
_quiet=0

function usage() {
    cat <<EOF
NAME
    $0 - from txt to pdf

SYNOPSIS
    $0 [OPTION] ... FILE

DESCRIPTION
    From txt to pdf... via html since, at this time
    libreoffice in headless mode can't permits setting
    so much parameters.

Formatting options:
    -c      column gap, default "15mm"
    -F      font family, default "sans-serif"
    -f      font size, default "10pt"
    -l      lineheight, default "1.4"
    -m      margin, default "15mm"
    -s      page size, default "A4"

Other Options:
    -q      quiet mode

EOF
}

while getopts "c:F:f:l:m:s:qh" arg
do
    case $arg in
        c)  _column_gap="$OPTARG"
            ;;
        F)  _font_family="$OPTARG"
            ;;
        f)  _font_size="$OPTARG"
            ;;
        l)  _line_height="$OPTARG"
            ;;
        m)  _margin="$OPTARG"
            ;;
        s)  _size="$OPTARG"
            ;;
	    q)  _quiet=1
	        ;;
	    # t)  t=1
	    #     ;;
        *|h)
	        usage
            exit 0
    esac
done
shift $(($OPTIND - 1))
input_file="$1"
tmp_file="${input_file%.*}.html"

if [ ! $_q ]; then 
    echo "converting $input_file (tmp_file is: $tmp_file)"
fi

# set | awk '$1 ~ /^_/ {print $1}'; exit 99

(echo "<html><head><style>@page { size: ${size}; margin: ${_margin}; } \
  body { column-gap: ${_column_gap}; font-family: ${_font_family}; \
  line-height: ${_line_height}; \
  font-size: ${_font_size}; white-space: pre-wrap; word-wrap: break-word; } \
  </style></head><body><pre>"; cat "$input_file"; echo '</pre></body></html>') \
  > "$tmp_file" && libreoffice --headless --convert-to pdf "$tmp_file"

rm "$tmp_file"
