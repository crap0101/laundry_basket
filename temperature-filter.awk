#!/usr/bin/awk -E

# temperature filter for the output
# of `sensors -u` with a vanilla sensors.conf
# (barely works without the -u option).
#
# author: Marco Chieppa | crap0101
# 2023

function reset() {
    name = ""
    description = ""
    in_block = 0
    use_tprint = 1
}
function tprint() {
    printf "*** %s (%s)\n", name, description
}
BEGIN {
    reset()
}

/^$/ {
    reset()
}

NF && in_block {
    description = $0
    if (use_tprint) {
        tprint()
	use_tprint = 0
    }
}

NF && !in_block {
    in_block = 1
    name = $0
    }

in_block && match($1, /^temp[0-9]+_(input|max):/, arr) {
    printf "  %s: %d °C\n", arr[1], $2
}

/^temp[0-9]+:|^MB Temp|^CPU Temp/ {
     use_tprint = 0
     printf "@%s\n", $0
}
