#!/bin/sh

PATH=/sbin:/bin:/usr/sbin:/usr/bin

pidfile=/var/run/twisted-pyanocktaild.pid rundir=/var/lib/twisted-pyanocktaild/ file=/etc/pyanocktaild.py logfile=/var/log/twisted-pyanocktaild.log

[ -r /etc/default/twisted-pyanocktaild ] && . /etc/default/twisted-pyanocktaild

test -x /usr/bin/twistd2.7 || exit 0
test -r $file || exit 0
test -r /usr/share/twisted-pyanocktaild/package-installed || exit 0


case "$1" in
    start)
        echo -n "Starting twisted-pyanocktaild: twistd"
        start-stop-daemon --start --quiet --exec /usr/bin/twistd2.7 --                           --pidfile=$pidfile                           --rundir=$rundir                           --python=$file                           --logfile=$logfile
        echo "."	
    ;;

    stop)
        echo -n "Stopping twisted-pyanocktaild: twistd"
        start-stop-daemon --stop --quiet              --pidfile $pidfile
        echo "."	
    ;;

    restart)
        $0 stop
        $0 start
    ;;

    force-reload)
        $0 restart
    ;;

    *)
        echo "Usage: /etc/init.d/twisted-pyanocktaild {start|stop|restart|force-reload}" >&2
        exit 1
    ;;
esac

exit 0
