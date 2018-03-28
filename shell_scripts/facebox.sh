#!/bin/bash

#Set variables
facebox_endpoint=$(awk '/facebox_endpoint/ {print $2}' /home/homeassistant/.homeassistant/secrets.yaml)
password=$(awk '/http_password/ {print $2}' /home/homeassistant/.homeassistant/secrets.yaml)
cameraURL=$(grep "$1_camera_image_url" /home/homeassistant/.homeassistant/secrets.yaml | awk '{print $2}')
sensor_name=$(grep "$1_faces_sensor" /home/homeassistant/.homeassistant/secrets.yaml | awk '{print $2}')

tagbox=$(curl -s -H 'Content-Type: application/json' -d '{"url": "'"$cameraURL"'"}' $facebox_endpoint)
tags=$(echo $tagbox | jq --raw-output '.facesCount')

curl -X POST -H "x-ha-access: $password" \
       -H "Content-Type: application/json" \
       -d '{"state":"'"$tags"'" }' \
       "$sensor_name"
