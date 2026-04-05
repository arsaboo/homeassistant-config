#!/bin/bash

wget -O /config/www/custom_ui/card-modder.js https://raw.githubusercontent.com/thomasloven/lovelace-card-modder/master/card-modder.js
sudo chown -R homeassistant:homeassistant /config/
