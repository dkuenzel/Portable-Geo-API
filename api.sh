#!/bin/sh

export FLASK_APP=/home/apiuser/app/mockup.py;
exec flask run --host=0.0.0.0;
