#!/bin/bash

wget -O /home/homeassistant/.homeassistant/www/custom_ui/card-modder.js https://raw.githubusercontent.com/thomasloven/lovelace-card-modder/master/card-modder.js
sudo chown -R homeassistant:homeassistant /home/homeassistant/.homeassistant/
