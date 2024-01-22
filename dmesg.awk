#!/usr/bin/env -S awk -E
#
# author: Marco Chieppa | crap0101
# version: 0.1
# date: 2024-01-22
# Copyright (C) 2024  Marco Chieppa
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


##########################################
# Prints dmesg log with a readable date. #
##########################################

function get_uptime() {
    getline < "/proc/uptime"
    close("/proc/uptime")
    return $1
}

function convert_time(uptime, from_uptime) {
    ttime = systime() - (uptime - from_uptime)
    return strftime("%a %b %d %H:%M:%S %T", ttime)
}

BEGIN {
    uptime = get_uptime()
    print uptime
    while (0 < (r = (getline < "/var/log/dmesg"))) {
	if (0 != match($0, /^\[\s*([0-9]+\.[0-9]+)\]/, record)) {
	    sub(/^\[\s*([0-9]+\.[0-9]+)\]/, "", $0)
	    print convert_time(uptime, record[1]) " " $0
	}
    }
    close("/var/log/dmesg")
}
