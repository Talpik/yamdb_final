#!/bin/sh
sudo docker exec -T yamdb_final_web_1 python3 manage.py migrate --noinput
sudo docker exec -T yamdb_final_web_1 python3 manage.py loaddata fixtures.json
sudo docker exec -T yamdb_final_web_1 python3 manage.py collectstatic --noinput
