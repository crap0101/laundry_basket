
@load "time"

# awk -f thisfile
# awk -v iter=NUM -f thisfile

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
        printf("%-8s %.2f%%\n",
               _fmt_name,
               (((_total_time_new - _total_time_old)       \
                - (_idle_new - _idle_old)) * 100)          \
	       / (_total_time_new - _total_time_old))
    }
}

function forever(num) {
    return 1
}

function iter_max(num) {
    return (num <= 0) ? 0 : 1
}

BEGIN {
    PROCINFO["sorted_in"] = "@ind_str_asc"
    STAT_FILE = "/proc/stat"
    STDERR = "/dev/stderr"
    
    cpuinfo()
    if (!iter) {
	loop = "forever"
	iter  = 0
    } else {
	if (!match(iter, /^[0-9]+$/)) {
	    printf("Invalid value for 'iter': <%s>\n", iter) > STDERR
	    exit 2
	} else {
	    loop = "iter_max"
	    iter += 0
	}
    }
    while (@loop(iter)) {
	move()
	sleep(0.5)
	cpuinfo()
	calc()
	iter -= 1
	print("*********")
    }
}
