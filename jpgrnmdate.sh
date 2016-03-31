for file in "$@"; do
    exiv2 -r'%Y-%m-%d_:basename:' $file
done
