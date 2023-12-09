#!/usr/bin/env -S awk -E

# author: Marco Chieppa | crap0101
# version: 0.1
# date: 2023-12-09
#
# Description:
# Reads a plain text file and outputs
# a formatted version suitable for use
# in the program's help() function.

@include "getopt"
# usually shipped with gawk
@include "awkpot"
# https://github.com/crap0101/awkpot

function help() {
    printf( \
	"Reads a plain text file and outputs a formatted version suitable" "\n"	\
	"for use in the program's help() function." "\n\n"	\
	"USAGE: %prog [FILE, ...]\n")
    awkpot::set_end_exit(0)
}

function version(progname, progversion) {
    printf("%s v%s\n", progname, progversion)
    awkpot::set_end_exit(0)
}

function parse_command_line() {
    Opterr = 1    # default is to diagnose
    Optind = 1    # skip ARGV[0]

    # parsing command line
    shortopts = "hv"
    longopts = "help,version"

    while ((c = getopt(ARGC, ARGV, shortopts, longopts)) != -1)
	switch (c) {
            case "h": case "help":
		help()
            case "v": case "version":
		version("format_help.awk", "0.1")
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


BEGIN {
    parse_command_line()
    printf("sprintf(")
}

{
    x = sprintf("\"%s\" \"\\n\"\\", awkpot::escape($0))
    printf("%s\n", x)
}

END {
    awkpot::end_exit()
    printf(")\n")
}


### For example:
# crap0101@orange:~/test$ cat cpuinfo.help 
# Display cpu(s) usage.
# Options:
#   -i, --iter=NUM
#     Max NUM of iterations. If NUM <=0 loops forever (default).
#   -m, --only-main
#     Display only the main cpu.
#   -s, --sleep=NUM
#     Sleep time between reading, in seconds. Default is 0.5.
#   -o, --overlap
#     In terminal that supported this, print on the same line
#     at each iteration.
#   -v, --version
#     Prints program's version.
#   -h, --help
#     Prints this help.
# crap0101@orange:~/test$ awk -f format_help.awk cpuinfo.help 
# sprintf("Display cpu(s) usage." "\n"\
# "Options:" "\n"\
# "  -i, --iter=NUM" "\n"\
# "    Max NUM of iterations. If NUM <=0 loops forever (default)." "\n"\
# "  -m, --only-main" "\n"\
# "    Display only the main cpu." "\n"\
# "  -s, --sleep=NUM" "\n"\
# "    Sleep time between reading, in seconds. Default is 0.5." "\n"\
# "  -o, --overlap" "\n"\
# "    In terminal that supported this, print on the same line" "\n"\
# "    at each iteration." "\n"\
# "  -v, --version" "\n"\
# "    Prints program's version." "\n"\
# "  -h, --help" "\n"\
# "    Prints this help." "\n"\
# )
# crap0101@orange:~/test$
