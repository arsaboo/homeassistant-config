#!/bin/bash

wget -O /home/homeassistant/.homeassistant/www/custom_ui/slider-entity-row.js https://raw.githubusercontent.com/thomasloven/lovelace-slider-entity-row/master/slider-entity-row.js
wget -O /home/homeassistant/.homeassistant/www/custom_ui/auto-entities.js https://raw.githubusercontent.com/thomasloven/lovelace-auto-entities/master/auto-entities.js
wget -O /home/homeassistant/.homeassistant/www/custom_ui/card-tools.js https://raw.githubusercontent.com/thomasloven/lovelace-card-tools/master/card-tools.js
wget -O /home/homeassistant/.homeassistant/www/custom_ui/layout-card.js https://raw.githubusercontent.com/thomasloven/lovelace-layout-card/master/layout-card.js
wget -O /home/homeassistant/.homeassistant/www/custom_ui/gap-card.js https://raw.githubusercontent.com/thomasloven/lovelace-gap-card/master/gap-card.js
wget -O /home/homeassistant/.homeassistant/www/custom_ui/config-template-card.js https://raw.githubusercontent.com/custom-cards/config-template-card/master/dist/config-template-card.js
wget -O /home/homeassistant/.homeassistant/www/custom_ui/card-modder.js https://raw.githubusercontent.com/thomasloven/lovelace-card-modder/master/card-modder.js
wget -O /home/homeassistant/.homeassistant/www/custom_ui/secondaryinfo-entity-row.js https://raw.githubusercontent.com/MizterB/lovelace-secondaryinfo-entity-row/master/secondaryinfo-entity-row.js
wget -O /home/homeassistant/.homeassistant/www/custom_ui/button-card.js https://raw.githubusercontent.com/custom-cards/button-card/master/button-card.js
wget -O /home/homeassistant/.homeassistant/www/custom_ui/calendar-card.js https://github.com/ljmerza/calendar-card/releases/download/3.10.0/calendar-card.js
sudo chown -R homeassistant:homeassistant /home/homeassistant/.homeassistant/
