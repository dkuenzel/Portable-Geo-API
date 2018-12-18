#!/bin/sh

ip=$(ifconfig eth0 | grep 'inet addr:' | sed -e 's_^[^0-9]\+:\([^ ]\+\).*$_\1_g');
echo "IP Address is: $ip";
export FLASK_APP=/home/apiuser/app/mockup.py;
exec flask run --host=0.0.0.0;
