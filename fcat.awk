#!/usr/bin/awk -E
#
# author: Marco Chieppa | crap0101
#


function usage(progname, sep) {
    printf "fcat -- USAGE \n" \
  "%s [-h|--help] [fsep=FORMAT_STRING] [file1, ...]\n" \
  "FORMAT_STRING is file separator string, default to '%s'\n" \
  "	        where %%s expand to the actually processed filename\n" \
  "\n", progname, gensub(/\n/, "\\\\n", "g", sep)
}

BEGIN {
    fsep="@@@ %s\n"
    for (i=i; i<ARGC; i++) {
	if (ARGV[i] == "-h" || ARGV[i] == "help") {
	    usage("fcat", fsep)
	    exit 0;
	} else if (match(ARGV[i], /^fsep=(.*)$/)) {
	    fsep=gensub(/^fsep=(.*)$/, "\\1", 1, ARGV[i])
	    fsep=gensub(/\\n/, "\\\n", "g", fsep)
	    delete ARGV[i]
	}
    }
}

BEGINFILE {printf fsep, FILENAME}

{}1

# EXAMPLE:
# crap0101@orange:~/test$ cat 1.txt 
# 1
# crap0101@orange:~/test$ cat 2.txt 
# 2
# crap0101@orange:~/test$ cat 1.txt 2.txt 
# 1
# 2
# crap0101@orange:~/test$ ./fcat 1.txt 2.txt 
# @@@ 1.txt
# 1
# @@@ 2.txt
# 2
# crap0101@orange:~/test$ ./fcat fsep='???\n' 1.txt 2.txt 
# ???
# 1
# ???
# 2
# crap0101@orange:~/test$ ./fcat fsep='??? %s ---\n' 1.txt 2.txt 
# ??? 1.txt ---
# 1
# ??? 2.txt ---
# 2
# crap0101@orange:~/test$ ./fcat fsep='' 1.txt 2.txt # like cat
# 1
# 2
