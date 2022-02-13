#!/bin/bash

#Set variables
tagbox_endpoint=$(awk '/tagbox_endpoint/ {print $2}' /config/secrets.yaml)
password=$(awk '/http_password/ {print $2}' /config/secrets.yaml)
cameraURL=$(grep "$1_camera_image_url" /config/secrets.yaml | awk '{print $2}')
sensor_name=$(grep "$1_tag_sensor" /config/secrets.yaml | awk '{print $2}')

tagbox=$(curl -s -H 'Content-Type: application/json' -d '{"url": "'"$cameraURL"'"}' $tagbox_endpoint)
tags=$(echo $tagbox | jq --raw-output '.tags | map(.tag) | join(", ")')

curl -X POST -H "x-ha-access: $password" \
       -H "Content-Type: application/json" \
       -d '{"state":"'"$tags"'" }' \
       "$sensor_name"
