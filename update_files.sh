#!/bin/bash

wget -O /home/homeassistant/.homeassistant/www/custom_ui/ext-weblink.js https://raw.githubusercontent.com/custom-cards/ext-weblink/master/ext-weblink.js
wget -O /home/homeassistant/.homeassistant/www/custom_ui/calendar-card.js https://raw.githubusercontent.com/rdehuyss/homeassistant-lovelace-google-calendar-card/master/calendar-card.js
wget -O /home/homeassistant/.homeassistant/www/custom_ui/slider-entity-row.js https://raw.githubusercontent.com/thomasloven/lovelace-slider-entity-row/master/slider-entity-row.js
wget -O /home/homeassistant/.homeassistant/www/custom_ui/alarm_control_panel-card.js https://raw.githubusercontent.com/ciotlosm/custom-lovelace/master/alarm_control_panel-card/alarm_control_panel-card.js
wget -O /home/homeassistant/.homeassistant/custom_components/media_player/alexa.py https://raw.githubusercontent.com/keatontaylor/custom_components/master/media_player/alexa.py
sudo chown -R homeassistant:homeassistant /home/homeassistant/.homeassistant/
