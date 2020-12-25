#!/bin/bash

MYIP=$(echo $SSH_CLIENT | awk '{print $1}')

echo Unbanning $MYIP
docker exec -t twitchbot_fail2ban fail2ban-client set traefik-auth unbanip $MYIP
