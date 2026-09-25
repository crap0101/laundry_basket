#!/bin/bash
# run ssh agent

# Copyright (C) 2026  Marco Chieppa aka crao9191

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not see <http://www.gnu.org/licenses/>


function ssh_check_and_run () {
    # It seemed simple,
    # it seemed safe,
    # it seemed stample
    # albeit it can wafe.
    # You're in a world of illusion
    # amid a reboot and a session,
    # where to use SSH
    # you just need to press play.
    function ssh_start_agent () {
        # @param: target socket
        printto "*** ssh: creating a new ssh agent"
        ssh-agent -s -a $2 | sed 's/^echo/#echo/' > $1
        chmod 600 $1
    }
    function update_ssh () {
        # @param: target sock pid
        printto "*** ssh: updating $1 with sock:$2 ; pid:$3"
        echo "SSH_AUTH_SOCK=$2; export SSH_AUTH_SOCK" > $1
        echo "SSH_AGENT_PID=$3; export SSH_AGENT_PID" >> $1
        chmod 600 $1
    }
    # files to save agent info and default socket
    if [ -n "$1" ]; then
        local target="$1"
    else
        local target="$HOME/.ssh/agent.env"
    fi
    if [ -n "$2" ]; then
        local static_socket="$2"
    else
        local static_socket="$HOME/.ssh/agent.sock"
    fi
    local do_update=0

    if [[ "$SSH_AUTH_SOCK" =~ .*keyring/ssh ]]; then
        # unset default value possibly created by gnome-keyring and alike
        printto "*** ssh: unset fucking keyring"
        unset SSH_AUTH_SOCK
    fi

    if [ ! -f "$target" ]; then
        # check if the default socket exists
        printto "*** ssh: no target file"
        ssh_start_agent $target $static_socket
    else
        # get the time from the last login and, if newer than the target file,
        # starts the agent ('cause probably we're reboot the system).
        local lastlog="$(loginctl show-session $XDG_SESSION_ID --property=Timestamp --value)"
        local logtime=$(date -d "$lastlog" +%s)
        local ttime=$(stat -c %X $target)

        if [ "$logtime" -gt "$ttime" ]; then
            printto "*** ssh: target file is old than this login session, start a new agent"
            ssh_start_agent $target $static_socket
        else
            local spid="$(awk -F '[=;]' '$1 ~ /^SSH_AGENT_PID/ {print $2}' $target)"
            local effective_spid=$(pgrep -nx ssh-agent)
            local proc_state=$(ps -eo pid,state | awk "\$1 == $effective_spid { print \$2 }")

            # check if pid's empty (for some reason)
            # and if the process is not a zombie or alike (non [ZT]).
            if [ -z "$effective_spid" ] || [[ $proc_state =~ ^[ZT]$ ]]; then
                printto "*** ssh: no pid or proc is zombie"
                ssh_start_agent $target $static_socket
            elif [ -z "$spid" ]; then
                printto "*** ssh: no pid found!"
                ssh_start_agent $target $static_socket
            else
                printto "*** ssh: saved/effective pid: $spid/$effective_spid"
                # NOTE: before using $static_socket... it's all so fragile...
                #local sock="$(awk -F '[=;]' '$1 ~ /^SSH_AUTH_SOCK/ {print $2}' $target)"
                #local effective_sock=$(find /tmp/ssh-* -user $USER -name "agent.*" -printf "%C@ %p\n" 2>/dev/null | sort -rn | head -n1 | awk '{print $2}')
                if [ "$spid" != "$effective_spid" ]; then
                    printto "*** ssh: wrong process id: $spid != $effective_spid (effective)"
                    export SSH_AGENT_PID=$effective_spid
                    (( do_update++ ))
                fi
            fi
        fi

        # NOTE: before using $static_socket; as above...
        # if [ "$sock" != "$effective_sock" ]; then
        #     echo "*** ssh: wrong socket: $sock != $effective_sock (effective)"
        #     export SSH_AUTH_SOCK=$effective_sock
        #     (( do_update++ ))
        # fi

        if [ "$do_update" -gt 0 ]; then
            update_ssh $target $SSH_AUTH_SOCK $SSH_AGENT_PID
        fi
    fi

    source $target

    # check with ssh-add
    ssh-add -l &>/dev/null
    local maybe_key=$?
    if [ $maybe_key -eq 2 ]; then
        printto "*** ssh: no ssh agent running here"
    elif [ $maybe_key -eq 1 ]; then
        printto "*** ssh: missing passphrase"
    else
        printto "*** ssh: agent running"
    fi

    # NOT WORKING ALONE (fuck gnome-keyring)
    unset SSH_ASKPASS
    unset GIT_ASKPASS
    export SSH_ASKPASS_REQUIRE=never
}

if [ "${BASH_SOURCE[0]}" = "$0" ]; then
    function usage () {
        cat <<HELP
SYNOPSIS: $(basename "$0") [OPTION]
DESCRIPTION: checks for a running ssh-agent, or runs a new one
    ...
    -e FILE    environment file, default to "$HOME/.ssh/agent.env"
    -s FILE    socket file, efault to "$HOME/.ssh/agent.env"
    -h         show this help and exit.

EXAMPLES:
* To see messages:
~$ PRINTTO_OUT=/dev/stdout $0
* To change files:
~$ $0 new_env_file new_socket_file
HELP
    }

    while getopts "e:s:h" arg
    do
        case $arg in
            e)  env_file="$OPTARG"
                ;;
            s)  sock_file="$OPTARG"
	            ;;
            *|h)
	        usage $0
            exit 0
        esac
    done
    shift $(($OPTIND - 1))

    for arg in "$@"
    do
        echo "WARNING: ignoring unknown argument $arg"
    done
    ssh_check_and_run "$env_file" "$sock_file"
else
    :
fi

unset usage env_file sock_file arg

