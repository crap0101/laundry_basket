#
# author: Marco Chieppa | crap0101
#

function usage () {
    cat <<HELP
DESCRIPTION:
    Renames given files to %Y-%m-%d_FILENAME where
    FILENAME is the original file name and
    %Y-%m-%d is the formatting string
    using definitions from strftime(3).
SYNOPSIS:
     $(basename "$0") [OPTION] PATH [PATH, ...]
OPTIONS:
    -f         custom format string
    -h         show this help and exit.
HELP
}

format_string='%Y-%m-%d_'
while getopts "f:h" arg
do
    case $arg in
	f)  format_string="$OPTARG"
	    ;;
    *|h)
	    usage "$0"
        exit 0
    esac
done
shift $(($OPTIND - 1))

if [ $# -eq 0 ]; then
    usage "$0"
    exit 1
fi

for file in "$@"; do
    exiv2 -r "${format_string}_:basename:" "$file"
done
