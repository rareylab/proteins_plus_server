#!/bin/bash
# start all processes needed to run the proteins.plus server

function get_vnc_displays () {
    TMP=$(mktemp)
    vncserver -list 2>&1 | grep -A 100 DISPLAY > $TMP
    NOF_DISPLAYS=$(expr $(cat $TMP | wc -l) - 1)
    cat $TMP | sed -r "s/\s.*//" | tail -n $NOF_DISPLAYS | sort
    rm $TMP
}

export DISPLAY=$(get_vnc_displays | head -n 1)

if [ -z "$DISPLAY" ] ; then
    echo "No available display found, starting vncserver"
    vncserver
    DISPLAY=$(get_vnc_displays | head -n 1)
else
    echo "Use display $DISPLAY from vncserver"
fi

if [ ! -f ./redis/redis_6378.pid ]; then
  echo 'start redis'
  redis-server ./redis/redis.conf
fi

if [ ! -f ./celery/run/proteins_plus_worker.pid ]; then
  echo 'start celery worker'
  celery -A proteins_plus multi start proteins_plus_worker --pidfile="$(pwd)/celery/run/%n.pid" --logfile="$(pwd)/celery/log/%n%I.log" --concurrency=16 --loglevel=INFO -O fair
fi

if [ ! -f ./gunicorn/gunicorn.pid ]; then
  echo 'start gunicorn'
  gunicorn --config gunicorn/gunicorn.conf.py proteins_plus.wsgi
fi

