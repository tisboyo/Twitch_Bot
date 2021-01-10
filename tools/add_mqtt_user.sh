#!/bin/bash
docker exec -it twitchbot_mqtt mosquitto_passwd -b /mosquitto/config/passwd $1 $2
