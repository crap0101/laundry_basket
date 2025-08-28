#!/bin/bash
# Converts seconds to time

# Copyright (C) 2025  Marco Chieppa | crap0101

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


function secs2time () {
    # $1: a number representing seconds
    # $2: (optional) if "1" print in machine-readable format as "DD:HH:MM:SS"
    #     printg days even if 0.
    #     Otherwise, when days are 0 print only "HH:MM:SS" or,
    #     when days are > 0 print "DD days HH:MM:SS"
    days=$(( $1 / (60*60*24) ))
    _dr=$(( $1 % (60*60*24) ))
    hours=$(( $_dr / (60*60) ))
    _dh=$(( $_dr % (60*60) ))
    minutes=$(( $_dh / 60 ))
    seconds=$(( $_dh % 60 ))
    if [ $days -eq 0 ]; then
	if [[ "$2" && "$2" -eq 1 ]]; then
	    printf "%02d:%02d:%02d:%02d\n" $days $hours $minutes $seconds
	else
	    printf "%02d:%02d:%02d\n" $hours $minutes $seconds
	fi
    else
	if [[ "$2" && "$2" -eq 1 ]]; then
	    printf "%02d:%02d:%02d:%02d\n" $days $hours $minutes $seconds
	else
	    printf "%d days %02d:%02d:%02d\n" $days $hours $minutes $seconds
	fi
    fi
}

secs2time "$1" "$2"
