#!/bin/bash

wget -O /home/homeassistant/.homeassistant/www/custom_ui/slider-entity-row.js https://raw.githubusercontent.com/thomasloven/lovelace-slider-entity-row/master/slider-entity-row.js
wget -O /home/homeassistant/.homeassistant/www/custom_ui/auto-entities.js https://raw.githubusercontent.com/thomasloven/lovelace-auto-entities/master/auto-entities.js
wget -O /home/homeassistant/.homeassistant/www/custom_ui/card-tools.js https://raw.githubusercontent.com/thomasloven/lovelace-card-tools/master/card-tools.js
wget -O /home/homeassistant/.homeassistant/www/custom_ui/button-card.js https://raw.githubusercontent.com/custom-cards/button-card/master/button-card.js
sudo chown -R homeassistant:homeassistant /home/homeassistant/.homeassistant/
