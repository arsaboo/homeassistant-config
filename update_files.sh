#!/bin/bash

wget -O /home/homeassistant/.homeassistant/www/custom_ui/slider-entity-row.js https://raw.githubusercontent.com/thomasloven/lovelace-slider-entity-row/master/slider-entity-row.js
wget -O /home/homeassistant/.homeassistant/custom_components/media_player/alexa.py https://raw.githubusercontent.com/keatontaylor/custom_components/master/media_player/alexa.py
wget -O /home/homeassistant/.homeassistant/www/custom_ui/button-card.js https://raw.githubusercontent.com/kuuji/button-card/master/button-card.js
wget -O /home/homeassistant/.homeassistant/www/custom_ui/auto-entities.js https://raw.githubusercontent.com/thomasloven/lovelace-auto-entities/master/auto-entities.js
wget -O /home/homeassistant/.homeassistant/www/custom_ui/card-tools.js https://raw.githubusercontent.com/thomasloven/lovelace-card-tools/master/card-tools.js
wget -O /home/homeassistant/.homeassistant/www/custom_ui/mini-media-player-bundle.js https://github.com/kalkih/mini-media-player/releases/download/v1.0.0/mini-media-player-bundle.js
wget -O /home/homeassistant/.homeassistant/www/custom_ui/mini-graph-card-bundle.js https://github.com/kalkih/mini-graph-card/releases/download/v0.3.0/mini-graph-card-bundle.js
sudo chown -R homeassistant:homeassistant /home/homeassistant/.homeassistant/
