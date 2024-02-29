#! /bin/bash

cd /content/server/gourmet-web
source venv/bin/activate
waitress-serve --port=4000 --call 'gourmetweb:create_app'
# cd ~/projects/dressage ; kill $(ps aux | grep waitress-serve | grep dressage:create_app | awk '{print $2}') ; source venv/bin/activate && waitress-serve --call 'dressage:create_app' 2>&1 >> ~/dressage.log &

exit 0
