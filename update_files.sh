#!/bin/bash

wget -O /home/homeassistant/.homeassistant/www/custom_ui/card-modder.js https://raw.githubusercontent.com/thomasloven/lovelace-card-modder/master/card-modder.js
wget -O /home/homeassistant/.homeassistant/custom_components/samsungtv/__init__.py https://raw.githubusercontent.com/tulindo/home-assistant/samsungtvws/homeassistant/components/samsungtv/__init__.py
wget -O /home/homeassistant/.homeassistant/custom_components/samsungtv/config_flow.py https://raw.githubusercontent.com/tulindo/home-assistant/samsungtvws/homeassistant/components/samsungtv/config_flow.py
wget -O /home/homeassistant/.homeassistant/custom_components/samsungtv/const.py https://raw.githubusercontent.com/tulindo/home-assistant/samsungtvws/homeassistant/components/samsungtv/const.py
wget -O /home/homeassistant/.homeassistant/custom_components/samsungtv/manifest.json https://raw.githubusercontent.com/tulindo/home-assistant/samsungtvws/homeassistant/components/samsungtv/manifest.json
wget -O /home/homeassistant/.homeassistant/custom_components/samsungtv/media_player.py https://raw.githubusercontent.com/tulindo/home-assistant/samsungtvws/homeassistant/components/samsungtv/media_player.py
wget -O /home/homeassistant/.homeassistant/custom_components/samsungtv/strings.json https://raw.githubusercontent.com/tulindo/home-assistant/samsungtvws/homeassistant/components/samsungtv/strings.json
wget -O /home/homeassistant/.homeassistant/custom_components/samsungtv/.translations/en.json https://raw.githubusercontent.com/tulindo/home-assistant/samsungtvws/homeassistant/components/samsungtv/.translations/en.json
wget -O /home/homeassistant/.homeassistant/custom_components/samsungtv/bridge.py https://raw.githubusercontent.com/tulindo/home-assistant/samsungtvws/homeassistant/components/samsungtv/bridge.py
sudo chown -R homeassistant:homeassistant /home/homeassistant/.homeassistant/
