#!/bin/bash

wget -O /home/homeassistant/.homeassistant/www/custom_ui/auto-entities.js https://raw.githubusercontent.com/thomasloven/lovelace-auto-entities/master/auto-entities.js
wget -O /home/homeassistant/.homeassistant/www/custom_ui/card-tools.js https://raw.githubusercontent.com/thomasloven/lovelace-card-tools/master/card-tools.js
wget -O /home/homeassistant/.homeassistant/www/custom_ui/layout-card.js https://raw.githubusercontent.com/thomasloven/lovelace-layout-card/master/layout-card.js
wget -O /home/homeassistant/.homeassistant/www/custom_ui/gap-card.js https://raw.githubusercontent.com/thomasloven/lovelace-gap-card/master/gap-card.js
wget -O /home/homeassistant/.homeassistant/www/custom_ui/card-modder.js https://raw.githubusercontent.com/thomasloven/lovelace-card-modder/master/card-modder.js
wget -O /home/homeassistant/.homeassistant/custom_components/samsungtv/__init__.py https://raw.githubusercontent.com/escoand/home-assistant/samsungtv_advance/homeassistant/components/samsungtv/__init__.py
wget -O /home/homeassistant/.homeassistant/custom_components/samsungtv/config_flow.py https://raw.githubusercontent.com/escoand/home-assistant/samsungtv_advance/homeassistant/components/samsungtv/config_flow.py
wget -O /home/homeassistant/.homeassistant/custom_components/samsungtv/const.py https://raw.githubusercontent.com/escoand/home-assistant/samsungtv_advance/homeassistant/components/samsungtv/const.py
wget -O /home/homeassistant/.homeassistant/custom_components/samsungtv/manifest.json https://raw.githubusercontent.com/escoand/home-assistant/samsungtv_advance/homeassistant/components/samsungtv/manifest.json
wget -O /home/homeassistant/.homeassistant/custom_components/samsungtv/media_player.py https://raw.githubusercontent.com/escoand/home-assistant/samsungtv_advance/homeassistant/components/samsungtv/media_player.py
wget -O /home/homeassistant/.homeassistant/custom_components/samsungtv/services.yaml https://raw.githubusercontent.com/escoand/home-assistant/samsungtv_advance/homeassistant/components/samsungtv/services.yaml
wget -O /home/homeassistant/.homeassistant/custom_components/samsungtv/strings.json https://raw.githubusercontent.com/escoand/home-assistant/samsungtv_advance/homeassistant/components/samsungtv/strings.json
sudo chown -R homeassistant:homeassistant /home/homeassistant/.homeassistant/
