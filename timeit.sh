#!/bin/bash

rep=1000
if [[ $1 =~ ^[0-9]+$ ]]; then
    rep=$1
    shift
fi

start=$(date +%s)
for i in $(seq 1 $rep); do
    "$@"
done
end=$(date +%s)

tot=$(expr $end - $start)
/usr/bin/printf "single: %.4f (tot: %.4f)\n" $(bc <<< "scale=4;$tot / $rep") $tot 1>&2
