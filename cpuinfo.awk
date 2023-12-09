#!/usr/bin/env -S awk -E
#
# author: Marco Chieppa | crap0101
# version: 0.2
# date: 2023-12-09
# Copyright (C) 2023  Marco Chieppa
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to
# deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
# sell copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
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

@load "time"
@include "getopt"
# usually shipped with gawk
@include "awkpot"
# https://github.com/crap0101/awkpot

function version(progname, progversion) {
    printf("%s v%s\n", progname, progversion)
    awkpot::set_end_exit(0)
}
function help() {
    printf("Display cpu(s) usage." "\n"	\
	    "Options:" "\n"			\
	    "  -i, --iter=NUM" "\n"					\
	    "    Max NUM of iterations. If NUM <=0 loops forever (default)." "\n" \
	    "  -m, --only-main" "\n"					\
	    "    Display only the main cpu." "\n"			\
	    "  -s, --sleep=NUM" "\n"					\
	    "    Sleep time between reading, in seconds. Default is 0.5." "\n" \
	    "    NUM <= 0 or crazy ones are silently reverted to the default value." "\n" \
	    "  -o, --overlap" "\n"					\
	    "    In terminal that supported this, print on the same line" "\n" \
	    "    at each iteration." "\n"				\
	    "  -v, --version" "\n"					\
	    "    Prints program's version." "\n"			\
	    "  -h, --help" "\n"						\
	    "    Prints this help." "\n")
    awkpot::set_end_exit(0)
}

function parse_command_line() {
    Opterr = 1    # default is to diagnose
    Optind = 1    # skip ARGV[0]

    # parsing command line
    shortopts = "i:ms:ohv"
    longopts = "iter:,only-main,sleep:,overlap,help,version"

    while ((c = getopt(ARGC, ARGV, shortopts, longopts)) != -1)
	switch (c) {
	    case "i": case "iter":
		iter = int(Optarg)
		break
	    case "m": case "only-main":
		only_main = 1
		break;
	    case "s": case "sleep":
		sleep_time = strtonum(Optarg)
		break
	    case "o": case "overlap":
		overlap = 1
		break
            case "h": case "help":
		help()
            case "v": case "version":
		version(PROGNAME, VERSION)
            case "?":
                # getopt_long already printed an error message.
	        printf("Explanation from %s: unknown option <%s>\n",
			ARGV[0], ARGV[Optind]) >> "/dev/stderr"
		exit(1)
            default:
		printf("%s: unknown option <%s>\n", ARGV[0], c) >> "/dev/stderr"
		exit(1)
	}
    # clear ARGV
    for (i = 1; i < Optind; i++)
        ARGV[i] = ""
}

function cpuinfo() {
    while (retcode = (getline < STAT_FILE)) {
	if (retcode < 0)
	{
	    printf("error reading from <%s>: %s\n", STAT_FILE, ERRNO) >> STDERR
	    close(STAT_FILE)
	    exit 1
	}
	if (match($0, /^cpu/))
	{
	    cpu_s[$1]["name"]["new"] = $1
	    cpu_s[$1]["user"]["new"] = $2
	    cpu_s[$1]["nice"]["new"] = $3
	    cpu_s[$1]["system"]["new"] = $4
	    cpu_s[$1]["idle"]["new"] = $5
	    cpu_s[$1]["__use"]["new"] = 0

	}
    }
    close(STAT_FILE)
}

function move() {
    for (cpu in cpu_s) {
	for (attr in cpu_s[cpu]) {
	    cpu_s[cpu][attr]["old"] = cpu_s[cpu][attr]["new"]
	}
    }
}

function calc() {
    for (cpu in cpu_s) {
	_fmt_name = cpu_s[cpu]["name"]["new"] ":"
	_total_time_new = (cpu_s[cpu]["user"]["new"]       \
			   + cpu_s[cpu]["nice"]["new"]     \
			   + cpu_s[cpu]["system"]["new"]   \
			   + cpu_s[cpu]["idle"]["new"])
	_total_time_old = (cpu_s[cpu]["user"]["old"]       \
			   + cpu_s[cpu]["nice"]["old"]     \
			   + cpu_s[cpu]["system"]["old"]   \
			   + cpu_s[cpu]["idle"]["old"])
	_idle_new = cpu_s[cpu]["idle"]["new"]
	_idle_old = cpu_s[cpu]["idle"]["old"]
        cpu_s[cpu]["__use"]["new"] = sprintf(              \
	    "%.2f",                                        \
	    (((_total_time_new - _total_time_old)	   \
	      - (_idle_new - _idle_old)) * 100)		   \
	    / (_total_time_new - _total_time_old))
    }
}

function print_calc (main, overlap,    end, tot) {
    end = overlap ? "\r" : "\n"
    if (main) {
	printf("%-6s %-6s%s",
	       cpu_s[main]["name"]["new"] ":",
	       cpu_s[main]["__use"]["new"] "%",
	       end)
    } else {
	tot = ""
	for (cpu in cpu_s) {
	    tot = tot sprintf("%-6s %-6s%s",
			      cpu_s[cpu]["name"]["new"] ":",
			      cpu_s[cpu]["__use"]["new"] "%",
			      overlap ? "|" : "\n")
	}
	printf("%s%s", tot, overlap ? end : "")
    }
}

function forever(num) {
    return 1
}

function iter_max(num) {
    return (num > 0)
}

function die_bad(reason, status) {
    printf("%s", reason) >> STDERR
    exit status
}

BEGIN {
    PROGNAME = "cpuinfo.awk"
    VERSION = "0.2"
    PROCINFO["sorted_in"] = "@ind_str_asc"
    STAT_FILE = "/proc/stat"
    STDERR = "/dev/stderr"
    sleep_time_default = 0.5
    overlap = 0

    parse_command_line()
    if  (! sleep_time)
	sleep_time = sleep_time_default
    if (! only_main)
	only_main = ""
    else
	only_main = "cpu"    
    if (! iter) {
	loop = "forever"
	iter = 0
    } else {
	loop = "iter_max"
    }

    cpuinfo()
    while (@loop(iter)) {
	move()
	sleep(sleep_time)
	cpuinfo()
	calc()
	print_calc(only_main, overlap)
	iter -= 1
	if (iter && ! overlap)
	    print("==========")
    }
    if (overlap)
	print ""
}
