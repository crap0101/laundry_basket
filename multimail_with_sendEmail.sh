#!/bin/bash
#
# author: Marco Chieppa | crap0101
#
# massive mail sender

function usage () {
    echo "
    -h    show this help and exit

    -a FILE   ATTACHMENT
    -f STR    sender email
    -l FILE   file with destinations emails (read from stdin otherwise)
    -m STR    email message
    -p STR    password (otherwise tou'll be prompted for it)
    -S SERVER[:PORT]    smtp mail relay. default to localhost:25   
    -s STR    email subject
    -u STR    username

BUGS:
    * attachments: filename with spaces == error
    * SSL connections: need some extra perl modules to work
"
}

nattach=0
declare -a attach


while getopts "S:p:a:m:s:f:u:l:" arg
do
    case $arg in
        a)
            attach[$nattach]=$(printf "%q" "$OPTARG")
            nattach=$((nattach+1))
            ;;
        f)
            from="$OPTARG"
            ;;
        l)
            maillist="$OPTARG"
            ;;
        m)
            message="$OPTARG"
            ;;
        p)
            password="$OPTARG"
            ;;
        S)
            server="$OPTARG"
            ;;
        s)
            subject="$OPTARG"
            ;;
        u)
            user="$OPTARG"
            ;;
        h)
            usage
            exit 0
            ;;
        *)
            usage
            exit 1
            ;;
    esac
done

if [ -z "$subject" ]
then
    echo -n "subject: "  
    read subject
fi

msgfile="$(tempfile)"
if [ -z "$message" ]
then
    ${EDITOR:-nano} "$msgfile"
else
    echo "$message" > "$msgfile"
fi

trap "rm -f $msgfile" SIGINT SIGTERM SIGKILL EXIT


if [ -z "$password" ]
then
    read -p "password: " -s password
    echo
fi

if [ -z "$maillist" ]
then
    maillist=/dev/stdin
fi

if [ $nattach -gt 0 ]
then
    with_attach="-a ${attach[@]}"
fi
 
retcode=0
#echo "!$@!" $(printf -- "%s" "$with_attach");exit
while read to
do
    sendEmail -f "$from" -xu "$user" -xp "$password" -s "$server" -t "$to" \
    -u "$subject" -o message-file="$msgfile" -o tls="yes" \
    -q $(printf -- "%s" "$with_attach")
    if [ $? -ne 0 ]
    then
        echo "$to send failed"
        retcode=$((retcode+1))
    fi
done < "$maillist"


exit $retcode
