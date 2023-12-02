#
# author: Marco Chieppa | crap0101
#

@load "time"

# bare use:
# $ awk -f thisfile
# max iterations (a positive integer. Default: loop forever)
# $ awk -v iter=NUM -f thisfile
# show the main cpu only
# $ awk -v main=1 -f thisfile
# choose sleep time (as seconds, a positive float or integer. Default: 0.5)
# $ awk -v wait=1.2 -f thisfile

function cpuinfo() {
    while (retcode = (getline < STAT_FILE)) {
	if (retcode < 0)
	{
	    printf("error reading from <%s>: %s\n", STAT_FILE,  ERRNO) > STDERR
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
        cpu_s[cpu]["__use"]["new"] = sprintf(                 \
	    "%.2f", \
	    (((_total_time_new - _total_time_old)	   \
	      - (_idle_new - _idle_old)) * 100)		   \
	    / (_total_time_new - _total_time_old))
    }
}

function print_calc (main) {
    if (main) {
	_fmt_name = cpu_s[main]["name"]["new"] ":"
	printf("%-8s %s%%\n", _fmt_name, cpu_s[cpu]["__use"]["new"])
    } else {
	for (cpu in cpu_s) {
	    _fmt_name = cpu_s[cpu]["name"]["new"] ":"
	    printf("%-8s %s%%\n", _fmt_name, cpu_s[cpu]["__use"]["new"])
	}
    }
}

function forever(num) {
    return 1
}

function iter_max(num) {
    return (num <= 0) ? 0 : 1
}

function die_bad(reason, status) {
    printf("%s", reason) > STDERR
    exit status
}

BEGIN {
    PROCINFO["sorted_in"] = "@ind_str_asc"
    STAT_FILE = "/proc/stat"
    STDERR = "/dev/stderr"
    sleep_time = 0.5

    if  (!wait && !length(wait)) {
	# keep default
    } else if (match(wait, /^[0-9]+(\.[0-9]+)?$/)) {
	if (wait == 0) {
	    die_bad(sprintf("Invalid value for 'wait': <%s>\n", wait), 2)
	} else {
	    sleep_time = wait + 0
	}
    } else {
	die_bad(sprintf("Invalid value for 'wait': <%s>\n", wait), 2)
    }

    if (!main) {
	only_main = ""
    } else if (match(main, /^1$/)) {
	only_main = "cpu"
    } else {
	die_bad(sprintf("Invalid value for 'main': <%s>\n", main), 2)
    }
    
    if (!iter) {
	loop = "forever"
	iter  = 0
    } else {
	if (!match(iter, /^[0-9]+$/)) {
	    die_bad(sprintf("Invalid value for 'iter': <%s>\n", iter), 2)
	} else {
	    loop = "iter_max"
	    iter += 0
	}
    }

    cpuinfo()
    while (@loop(iter)) {
	move()
	sleep(sleep_time)
	cpuinfo()
	calc()
	print_calc(only_main)
	iter -= 1
	if (iter) {
	    print("*********")
	}
    }
}
