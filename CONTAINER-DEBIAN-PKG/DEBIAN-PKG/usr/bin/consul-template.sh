#!/bin/bash

set -e

function start() {
    # When a change in the Consul catalog is detected, consul-template-config.hcl is executed by consul-template.
    /usr/bin/consul-template -config=/etc/consul.d/templates/
}

function stop() {
    ps=$(ps aux | grep consul-template | grep -v grep | awk '{print $2}')
    if [ -n "$ps" ]; then
        kill -9 $ps
    fi
}

function restart() {
    stop
    sleep 1
    start
}

case $1 in
        start)
            start
            ;;

        stop)
            stop
            ;;

        restart)
            stop
            start
            ;;

        *)
            echo $"Usage: $0 {start|stop|restart}"
            exit 1
esac

exit 0
