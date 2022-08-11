#!/bin/bash
# check the server is running correctly

# only run if there is not already an error
if [ ! -s check_error.txt ]; then

  python3 manage.py check_server $FULL_URL &> check_error.txt

  if [ -s check_error.txt ]; then
    cat check_error.txt
  fi
fi
