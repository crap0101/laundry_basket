#!/usr/bin/env -S awk -E

@include "getopt"
# usually shipped with gawk
@include "awkpot"
# https://github.com/crap0101/awkpot

# For each FILE, print to stdout each input lines N times.

# Copyright (C) 2025 Marco CHieppa (aka crap0101)

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not see <http://www.gnu.org/licenses/>   

function help() {
    printf("" "\n"				\
	   "%s v.%s\n"				\
	   "SYNOPSYS:" "\n"	                \
	   "     %s [OPTION] [FILE]..." "\n"	\
	   "DESCRIPTION" "\n"		\
	   "     For each FILE, print to stdout each input lines N times." "\n"	\
	   "     -n, --number" "\n"					\
	   "         repeat lines N times (default 2)." "\n"		\
	   "     -h, --help" "\n"		\
	   "       Print this help.    " "\n"	\
	   "     -v, --version" "\n"		\
	   "       Print the program version." "\n",
	   PROGNAME, PROGVERSION, PROGNAME)
    awkpot::set_end_exit(0)
}

function version() {
    printf("%s v.%s\n", PROGNAME, PROGVERSION)
    awkpot::set_end_exit(0)
}

function parse_command_line() {
    Opterr = 1    # default is to diagnose
    Optind = 1    # skip ARGV[0]

    # parsing command line
    shortopts = "n:hv"
    longopts = "number:,help,version"

    while ((c = getopt(ARGC, ARGV, shortopts, longopts)) != -1)
	switch (c) {
	    case "n": case "number":
		if (Optarg !~ /[0-9]+/) {
		    printf("%s: ERROR: <%s>: not a number (must be [0-9]+)\n", PROGNAME, Optarg) >> "/dev/stderr"	
		    awkpot::set_end_exit(1)
		}
		REPEATS = int(Optarg)
		break
            case "h": case "help":
		help()
            case "v": case "version":
		version()
            case "?":
                # getopt_long already printed an error message.
	        printf("Explanation from %s: unknown option <%s>\n",
			PROGNAME, ARGV[Optind-1]) >> "/dev/stderr"
		awkpot::set_end_exit(1)
            default:
		printf("%s: unknown option <%s>\n", PROGNAME, c) >> "/dev/stderr"
		awkpot::set_end_exit(1)
	}
    # clear ARGV
    for (i = 1; i < Optind; i++)
        ARGV[i] = ""
}


BEGIN {
    PROGNAME = "repeat.awk"
    PROGVERSION = "0.1"
    REPEATS = 2
    parse_command_line()
}


{
    for (i=0; i<REPEATS; i++)
	print($0)
}


END {
    awkpot::end_exit()
}
