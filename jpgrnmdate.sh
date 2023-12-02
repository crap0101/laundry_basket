#
# author: Marco Chieppa | crap0101
#
for file in "$@"; do
    exiv2 -r'%Y-%m-%d_:basename:' $file
done
