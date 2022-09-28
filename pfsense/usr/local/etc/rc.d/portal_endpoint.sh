#!/bin/sh
# This file was automatically generated
# by the pfSense service handler.

rc_start() {
        echo "starting portal_endpoint daemon..."
        /usr/local/sbin/portalendpoint.py
        echo "done"
}

rc_stop() {
        target_pid=$(cat /var/run/portal_endpoint.pid)
        if [ "${target_pid}" == "" ]
        then
                echo "no pid found for portal_endpoint"
        else
                kill $target_pid
        fi
        # Just to be sure...
        sleep 3
        #ps auxwww | grep -iE portal_endpoint | grep -v grep |  awk '{print $2}' | xargs -I@ kill @

}

case $1 in
        start)
                rc_start
                ;;
        stop)
                rc_stop
                ;;
        restart)
                rc_stop
                rc_start
                ;;
esac