#!/usr/bin/env -S awk -E

# author: Marco Chieppa | crap0101
# version: 0.1
# date: 2023-12-09
#
# Description:
# Reads a plain text file and outputs
# a formatted version suitable for use
# in the program's help() function.


@include "awkpot"
# https://github.com/crap0101/awkpot




BEGIN {
    printf("sprintf(")
}

{
    x = sprintf("\"%s\" \"\\n\"\\", awkpot::escape($0))
    printf("%s\n", x)
}

END {
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
