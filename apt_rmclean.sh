#!/bin/bash

interactive=0

function help () {
    echo 'run in sequence apt-get commands (autoremove, clean)'
    echo "usage: % $1 [-i]"
    echo "-h    show this help"
    echo "-i    ask for password"
}

function run_with_sudo () {
    sudo "$1"
}

while getopts "hi" arg
do
    case $arg in
        h) help `basename "$0"`; exit;;
        i) interactive=1;;
        *) exit 1;;
    esac
done

if [ $UID != 0 ]; then
    if  [ $interactive == 0 ]; then
        echo "you must be root"
        exit 1
    else
        run_with_sudo "$0"
    fi
else
    apt-get autoremove && apt-get clean
fi
