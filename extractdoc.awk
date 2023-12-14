#!/usr/bin/env -S awk -E

@include "getopt"
# usually shipped with gawk
@include "awkpot"
# https://github.com/crap0101/awkpot


# This bunch of lines are the module "description",
# from the first commented line (above)
# until the last commented line.
# Commented line must be consecutive, without
# intermixed blank lines even.
# A "description" commented lines is one that match /^\s*#/ .
# Function doc starts from the line next to the one
# where the `function' (or `func', if not in posix mode) keyword
# has been found, until the line which not match the
# regular expression /^\s*#\s*/.
# If the first doc line starts with "#[NODOC]"
# the doc will be ignored for that function.
# NOTE: right now multiline definitions as in:
# function foobar (a, b,
#                  c, d) {
#    # It's foobar
# }
# are not fully supported, can be some formatting issues and blanks at
# the end of the lines can cause to interpreter some parameter as local...
# that's because "locals" are recognized following the coding convention
# of add extra space before them (default to 4 spaces).

# This is NOT a global doc line.

## SAMPLE FUNC DEF ##
function foo (a, b, c) {}
function foo2(a, b, c) {
    #[NODOC]
    # this lines
    # will be
    # ignored
}
	 
function bar () {
  ## bar doc
}

function bar2() {
  # bar2 doc
  # bar2 doc line 2
  # bar2 doc line 3

  # NO doc line 4
}

function spam (a,   x) {
    #spam doc
    x = a
    # NO DOC!
    return x
}

func spam2(a,   x, y) {  
}

func spam3(a,   x, y) {  
    # Like <spam2> this function is show
    # only when --no-posix-mode is in effect.
}

function _private (x, y, z) {
    # private doc
}

function multiline_f(a, b, c,
		     d, e, f,
		     g,    h) {
    # multi doc
}
function multiline_f2(a, b, c,    # blanks at the end of the line makes
		      d, e, f,    # the following parameter to be "local"
		      g, h) {
}
## END OF SAMPLE FUNC DEF ##

function help() {
    printf("" "\n"							\
"%s v.%s\n" "\n"\
"Extract documentation from an awk source file.\n" "\n" \
"The first bunch of commented out lines (shebang excluded) are the" "\n" \
"module \"description\", used for general information about the program itself." "\n"\
"Commented line must be consecutive, without intermixed blank lines even." "\n"\
"A \"description\" lines is one that match /^\\s*#/ ." "\n"\
"Function docstrings starts from the line next to the one where the `function'" "\n"\
"(or even `func', if not in posix mode) keyword has been found, until the line" "\n"\
"which not match the regular expression /^\\s*#\\s*/ ." "\n"\
"If the first function's docstring line starts with \"#[NODOC]\", then" "\n"\
"the docstring will be ignored for that function." "\n"\
"NOTE: right now multiline definitions as in:" "\n"\
"function foobar (a, b," "\n"\
"                 c, d) {" "\n"\
"   It's foobar" "\n"\
"}" "\n"\
"are not fully supported: can be some formatting issues and blanks at the end" "\n"\
"of the lines can cause to interpreter some parameter as locals... that's" "\n"\
"because \"locals\" are recognized following the coding convention of add extra" "\n"\
"spaces before them (default to 4 spaces)." "\n"\
"" "\n"\
"" "\n"\
"    -d, --nodoc," "\n"\
"      Do not get nor print docstrings." "\n"\
"    -D, --no-description" "\n"\
"      Do not print the module description." "\n"\
"    -e, --exclude REGEX" "\n"\
"      Skip funtions which name matches REGEX." "\n"\
"    -f, --only-name" "\n"\
"      Print the function names only." "\n"\
"    -F, --print-filename" "\n"\
"      Prepend the file name on output." "\n"\
"     -l, --include-locals" "\n"\
"       Include the function's local parameters." "\n"\
"     -i, --indent STR" "\n"\
"       Indent the docstring with STR (default 4 spaces)." "\n"\
"     -o, --outfile FILE" "\n"\
"       Output on FILE. Default is to print on stdout." "\n"\
"     -O, --outfile-suffix STR" "\n"\
"       Write a file for each input file, naming them FILENAME.STR" "\n"\
"    -p, --no-posix-mode" "\n"\
"      Recognize 'func' as a valid keyword for function definition." "\n"\
"     -s, --sort STR" "\n"\
"       Sort with the mode specified by STR, which must match /[adr]/" "\n"\
"       'a' stands for ascending, 'd' for descending, with 'r'" "\n"\
"       functions are printed in the order were read." "\n"\
"     -h, --help" "\n"\
"       Print this help.    " "\n"\
"     -v, --version" "\n"\
"       Print the program version." "\n",
	   PROGNAME, PROGVERSION)
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
    shortopts = "dDe:fFi:lo:O:s:phv"
    longopts = "nodoc,no-description,exclude:,include-locals,indent:,only-name,"
    longopts = longopts "outfile:,outfile-suffix:no-posix-mode,sort:,"
    longopts = longopts "print-filename,help,version"
    
    while ((c = getopt(ARGC, ARGV, shortopts, longopts)) != -1)
	switch (c) {
	    case "d": case "nodoc": # do not get nor print docstring
		global_no_doc = 1
		break
	    case "D": case "no-description":
		no_description = 1
		break
	    case "e": case "exclude":
		exclude_regex = Optarg
		break
	    case "f": case "only-name":
		names_only = 1
		break
	    case "F": case "print-filename": # prepend the filename on output
		print_filename = 1
		break
	     case "l": case "include-locals":
	     	include_locals = 1
	     	break
	     case "i": case "indent": # indent docstring
	     	indent = Optarg
	     	break
	     case "o": case "outfile":
	     	outfile = Optarg
	     	break
             # write a file for each input file, naming them FILENAME.suffix
	     case "O": case "outfile-suffix":
	     	outfile_each_suffix = Optarg
	     	break
	    case "p": case "no-posix-mode":
		posix_mode = 0
		break;
	     case "s": case "sort": # /[adr]/ # ascending, descending, as read
	     	sort_order = Optarg
	     	break
            case "h": case "help":
		help()
            case "v": case "version":
		version()
            case "?":
                # getopt_long already printed an error message.
	        printf("Explanation from %s: unknown option <%s>\n",
			ARGV[0], ARGV[Optind]) >> "/dev/stderr"
		awkpot::set_end_exit(1)
            default:
		printf("%s: unknown option <%s>\n", ARGV[0], c) >> "/dev/stderr"
		awkpot::set_end_exit(1)
	}
    # clear ARGV
    for (i = 1; i < Optind; i++)
        ARGV[i] = ""
}


function get_func_name(s) {
    if (index(s, "("))
	return substr(s, 1, index(s, "(") - 1)
    else
	return s
}


function get_func_def(s, include_locals,    name, arr, sn, oldrs) {
    if (! index(s, ")")) {
	oldrs = RS
	RS = ")"
	awkpot::getline_or_die(FILENAME, 1)

	#s = s " " awkpot::get_record_string() ")"
        #gsub(/\s*\n\s*/, "", s) #+1
        #gsub(/\s*/, "", s)      #+2

	gsub(/#.*$/, "", s)
	sn = awkpot::get_record_string()
	split(sn, arr, "\n")
	for (i in arr) {
	    gsub(/^\s*/, "", arr[i]) # removes leading blanks
	    gsub(/#.*$/, "", arr[i]) # removes any comment
	}
	sn = awkpot::join(arr, " ", "@ind_num_asc")
	s = s " " sn ")" # add the ) chomped before, needed at the end

	# get the (unused) last chunk of the current line, so as
	# the next record reading is clean
	RS = oldrs
	awkpot::getline_or_die(FILENAME, 1)
	delete arr
    }
    if (! include_locals) {
	name = get_func_name(s)
	sub(name, "", s)
	split(s, arr, /(\s{4,}|\))/)
	if (match(arr[1], /.*,$/))
	    return name substr(arr[1], 1, length(arr[1])-1) ")"
	return name substr(arr[1], 1, length(arr[1])) ")"
    } else
	return substr(s, 1, index(s, ")"))
}

BEGIN {
    # INTERNALS
    PROGNAME = "extractdoc.awk"
    PROGVERSION = "0.1"
    # some defaults
    exclude_regex = ""
    global_no_doc = 0
    include_locals = 0
    indent = "    "
    no_description = 0
    posix_mode = 1
    sort_order = "r"
    #outfile_suffix = FILENAME ".extdoc"

    parse_command_line()
    if (sort_order !~ /[adr]/) {
	printf("wrong value for -s/--sort option: <%s>\n", sort_order) > "/dev/stderr"
	awkpot::set_end_exit(1)
    }
    if (outfile && outfile_each_suffix) {
	printf("Options conflict: -o/-O\n") > "/dev/stderr"
	awkpot::set_end_exit(1)
    }
    if (! outfile)
	outfile = "/dev/stdout"
    
    if (posix_mode)
	funmatch = @/^function$/
    else
	funmatch = @/^func(tion)?$/
}

BEGINFILE {
    delete funclist
    _description = ""
    _end_descr = no_description
    _fcurr = ""
    _nodoc = 0
    _idx = 0
    if (outfile_each_suffix)
	outfile = FILENAME outfile_each_suffix
}


$0 ~ /^#!/ && FNR == 1 {
    # skip shebang
    next
}

$0 ~ /^\s*#/ && (! _fcurr) && (! _end_descr) {
    sub(/^\s*#*\s*/, "")
    _description = sprintf("%s%s\n", _description, $0)
    next
}

$1 ~ funmatch {
    fname = get_func_name($2)
    if (exclude_regex && (fname ~ exclude_regex)) {
	#print("skippig:", fname)
	next
    }
    s = awkpot::get_record_string(2)
    fdef = get_func_def(s, include_locals)
    _idx += 1
    funclist[_idx]["name"] = fname
    funclist[_idx]["def"] = fdef
    funclist[_idx]["doc"] = ""
    _fcurr = fname
    next
}

$1 ~ /#\[NODOC\]/ {
    _nodoc = 1
    next
}

$1 ~ "#" && _fcurr && (! _nodoc) && (! global_no_doc) {
    sub(/^\s*#\s*/, "")
    funclist[_idx]["doc"] = sprintf("%s%s%s\n", funclist[_idx]["doc"], indent, $0)
    next
}

{
    _fcurr = ""
    _nodoc = 0
    if (_description)
	_end_descr = 1
}

function sort_by_name_asc(i1, v1, i2, v2) {
    if (v1["name"] < v2["name"])
        return -1
    if (v1["name"] > v2["name"])
        return 1
    return 0
}
function sort_by_name_desc(i1, v1, i2, v2) {
    if (v1["name"] > v2["name"])
        return -1
    if (v1["name"] < v2["name"])
        return 1
    return 0
}

ENDFILE {
    if (sort_order == "a")
	awkpot::set_sort_order("sort_by_name_asc")
    else if (sort_order == "d")
	awkpot::set_sort_order("sort_by_name_desc")
    else 
	awkpot::set_sort_order("@ind_num_asc")

    if (print_filename)
	printf("#file:%s\n", FILENAME) >> outfile
    if (! no_description)
	printf("=== DESCRIPTION  ===\n%s=========\n", _description) >> outfile
    for (i in funclist) {
	if (names_only)
	    print funclist[i]["name"] >> outfile
	else
	    print funclist[i]["def"] >> outfile
	if (! global_no_doc)
	    print funclist[i]["doc"] >> outfile
    }
}

END {
    awkpot::end_exit()
}
