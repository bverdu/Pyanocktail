#!/bin/sh

PATH=/sbin:/bin:/usr/sbin:/usr/bin

pidfile=/var/run/pianocktail.deb.pid rundir=/var/lib/pianocktail.deb/ file=/etc/pyanocktaild.py logfile=/var/log/pianocktail.deb.log

[ -r /etc/default/pianocktail.deb ] && . /etc/default/pianocktail.deb

test -x /usr/bin/twistd2.7 || exit 0
test -r $file || exit 0
test -r /usr/share/pianocktail.deb/package-installed || exit 0


case "$1" in
    start)
        echo -n "Starting pianocktail.deb: twistd"
        start-stop-daemon --start --quiet --exec /usr/bin/twistd2.7 --                           --pidfile=$pidfile                           --rundir=$rundir                           --python=$file                           --logfile=$logfile
        echo "."	
    ;;

    stop)
        echo -n "Stopping pianocktail.deb: twistd"
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
        echo "Usage: /etc/init.d/pianocktail.deb {start|stop|restart|force-reload}" >&2
        exit 1
    ;;
esac

exit 0
