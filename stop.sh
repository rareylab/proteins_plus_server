# end processes started with the start.sh in the reverse order of starting them to avoid errors

if [ -f ./gunicorn/gunicorn.pid ]; then
  echo 'stop gunicorn'
  kill $(cat ./gunicorn/gunicorn.pid)
fi

if [ -f ./celery/run/proteins_plus_worker.pid ]; then
  echo 'stop celery worker'
  celery -A proteins_plus multi stop proteins_plus_worker --pidfile="$(pwd)/celery/run/%n.pid" --logfile="$(pwd)/celery/log/%n%I.log" --loglevel=INFO
fi

if [ -f ./redis/redis_6378.pid ]; then
  echo 'stop redis'
  redis-cli -p 6378 shutdown
fi

