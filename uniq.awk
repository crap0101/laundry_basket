#!/usr/bin/env -S awk -E

# Name: uniq.awk
# Version: 0.1
# Author: Marco Chieppa | crap0101
# Last Update: 2023-12-06
# Description: uniq's quasi-clone.
# Requirement:
#     gawk >= 5.1.0
#     getopt: usually shipped with gawk
#     awkpot: https://github.com/crap0101/awkpot

# Copyright (C) 2023  Marco Chieppa | crap0101

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

@include "getopt"
@include "awkpot"

function _help(progname, version) {
    return sprintf(\
"%s v.%s" "\n"\
"A uniq quasi-clone, with some options added and others missing!" "\n"\
"  -c, --count" "\n"\
"    Prefix lines by number of occurrences." "\n"\
"  -F, --fields-separator=STR" "\n"\
"    A character or a multichar string (which can be interpreted as a" "\n"\
"    regular expression) for field-splitting input lines." "\n"\
"    By default the gawk's default FS value is used." "\n"\
"  -O, --out-fields-separator=STR" "\n"\
"    String separator between fields (actually used only with the -c option)." "\n"\
"  -f, --skip-fields=N" "\n"\
"    Avoid comparing the first N fields." "\n"\
"  -W, --check-fields=N" "\n"\
"    Compares until the Nth field included." "\n"\
"  -i, --ignore-case" "\n"\
"    Case-insensitive comparison." "\n"\
"  -s, --skip-chars=N" "\n"\
"    Avoid comparing the first N characters." "\n"\
"  -w, --check-chars=N" "\n"\
"    Comparing until the Nth character included." "\n"\
"  -u, --unique" "\n"\
"    Only print unique lines." "\n"\
"  -z, --zero-terminated" "\n"\
    "Line delimiter is NUL." "\n"\
"  -Z, --zero-terminated-output" "\n"\
    "Output line delimiter is NUL." "\n"\
"  -r, --records-separator=STR" "\n"\
"    A character or a multichar string (which can be interpreted as a" "\n"\
"    regular expression) for record-splitting input lines." "\n"\
"  -R, --out-records-separator=STR" "\n"\
    "Output line delimiter is STR." "\n"\
"  -h, --help" "\n"\
"    Prints this help and exits." "\n"\
"  -v, --version" "\n"\
"    Prints the program version and exits." "\n"\
"  * NOTE_1: Fields are skipped before chars." "\n"\
"  * NOTE_2: -R and -O options supports a limited set of escape sequences" "\n"\
"  * which can be used for a sensible output. Right now are supported:" "\n"\
"   \"\\0\", \"\\n\", \"\\a\", \"\\b\", \"\\f\", \"\\r\", \"\\t\", \"\\v\"." "\n"\
"    Any other backslash sequence will be printed literally." "\n",
progname, version)
}
function help() {
    printf("%s\n", _help(_PROGNAME, _VERSION)) >> "/dev/stderr"
    awkpot::set_end_exit(1)
}
function version() {
    printf("%s %s\n", _PROGNAME, _VERSION) >> "/dev/stderr"
    awkpot::set_end_exit(0)
}

function parse_command_line() {
    Opterr = 1    # default is to diagnose
    Optind = 1    # skip ARGV[0]

    # parsing command line
    shortopts = "cF:O:f:is:r:R:uw:W:zZhv"
    longopts = "count,fields-separator:,out-fields-separator:,skip-fields:,"
    longopts = longopts "check-fields:,ignore-case,skip-chars:,check-chars:,"
    longopts = longopts "unique,zero-terminated,zero-terminated-output,"
    longopts = longopts "records-separator:,out-records-separator:,"
    longopts = longopts "help,version"

    while ((c = getopt(ARGC, ARGV, shortopts, longopts)) != -1)
	switch (c) {
	    case "c": case "count":
		count = 1
		break
	    case "F": case "fields-separator":
	     	fields_separator = Optarg
	     	break
	    case "O": case "out-fields-separator":
	     	out_fields_separator = Optarg
	     	break
	    case "f": case "skip-fields":
	     	skip_fields_n = int(Optarg)
	     	break
	    case "W": case "check-fields":
	     	until_fields_n = int(Optarg)
	     	break
	    case "i": case "ignore-case":
	     	no_case = 1
	     	break
	    case "s": case "skip-chars":
		# we add one since this will be always passed to substr()
	     	skip_chars_n = int(Optarg) + 1
	     	break
	    case "w": case "check-chars":
	     	until_chars_n = int(Optarg)
	     	break
	    case "u": case "unique":
	     	unique = 1
	     	break;
	    case "z": case "zero-terminated":
	     	zeroes = 1
	     	break;
	    # options -z and -Z differs from the original uniq
	    # since we can choice to read/write null-delimited
	    # records independently.
	    case "Z": case "zero-terminated-output":
	     	zero_out = 1
	     	break;
	    case "r": case "records-separator":
	     	records_separator = Optarg
	     	break
	    case "R": case "out-records-separator":
	     	out_records_separator = Optarg
	     	break
            case "h": case "help":
		help()
            case "v": case "version":
		version()
            case "?":
                # getopt_long already printed an error message.
	        printf("Explanation from %s: unknown option <%s>\n",
			ARGV[0], ARGV[Optind]) >> "/dev/stderr"
		awkpot::set_end_exit(1)
            default:
		printf("%s: unknown option <%s>\n", ARGV[0], c) >> "/dev/stderr"
		awkpot::set_end_exit(1)
	}
    if (unique && count) {
	print("Conflict: -c/--count and -u/--unique options") >> "/dev/stderr"
	awkpot::set_end_exit(1)
    }
    if (zeroes && awkpot::check_assigned(records_separator)) {
	print("Conflict: -z and -r options") >> "/dev/stderr"
	awkpot::set_end_exit(1)
    }
    if (zero_out && awkpot::check_assigned(out_records_separator)) {
	print("Conflict: -Z and -R options") >> "/dev/stderr"
	awkpot::set_end_exit(1)
    }

    # clear ARGV
    for (i = 1; i < Optind; i++)
        ARGV[i] = ""
}


# PRINTING (option --count)
function print_count(item) {
    print last_count, item
}

# PRINTING (no option)
function print_line(item) {
    print item
}

# PRINTING (option --unique)
function print_unique(item) {
    if (last_count == 1)
	print item
}

# get the string (options --skip-chars and --check-chars)
function skip_chars(s) {
    return substr(s, skip_chars_n, until_chars_n ? until_chars_n : length(s))
}

# get the record's string, skipping fields (option --skip-fields)
function skip_fields() {
    if ((! skip_fields_n) && (! until_fields_n))
	return $0
    # we add 1 since get_record_string returns the fields from..to inclusively
    return awkpot::get_record_string(skip_fields_n + 1, until_fields_n)
}

# DO THE JOB
function __filter() {
    __current = skip_chars(skip_fields())
    return __current
}


BEGIN {
    _PROGNAME = "uniq.awk"
    _VERSION = "0.1"
    parse_command_line()
    _print = "print_line"
    if (count)
	_print = "print_count"
    if (unique)
	_print = "print_unique"

    # NOTE: using "\0" is not portable, as per
    # https://www.gnu.org/software/gawk/manual/html_node/gawk-split-records.html
    # but seems the uniq way (pun intended).
    if (awkpot::check_assigned(records_separator))
	RS = records_separator
    if (zeroes)
	RS = "\0"
    if (awkpot::check_assigned(out_records_separator)) 
	ORS = awkpot::make_printable(out_records_separator)
    if (zero_out)
	ORS = "\0"
    if (awkpot::check_assigned(fields_separator))
	FS = fields_separator
    if (awkpot::check_assigned(out_fields_separator))
	OFS = awkpot::make_printable(out_fields_separator)
    if (no_case)
	IGNORECASE = 1
    
    if (1 == (r = (getline))) {
	last_count = 1
	__last = __filter()
	last = $0
    } else {
	if (r == 0)
	    awkpot::set_end_exit(0)
	else
	    printf("Very very strange error with <%s>\n", FILENAME) >> "/dev/stderr"
	    awkpot::set_end_exit(1)
    }
}

__filter() != __last {
    @_print(last)
    __last = __current
    last = $0
    last_count = 1
    next
}

__filter() == __last {
    last_count += 1
}

END {
    awkpot::end_exit()
    @_print(last)
}
