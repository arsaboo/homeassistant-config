# Home Assistant Configuration

Here's my [Home Assistant](https://home-assistant.io/) configuration. I have installed HA on an [Intel NUC SkullCanyon](https://www.amazon.com/dp/B01DJ9XS52/) with [32GB RAM](https://www.amazon.com/gp/product/B015YPB8ME/) and [500GB NVMe SSD](https://www.amazon.com/gp/product/B01LYFKJR7/). I am currently running Ubuntu 16.04 LTS on the NUC and used the [virtual environment](https://home-assistant.io/docs/installation/virtualenv/) approach to install HA.

I regularly update my configuration files. You can check my current HA version [here](.HA_VERSION). If you like anything here, Be sure to :star2: my repo!

## Other things that I run on my NUC

* [Home Assistant](https://home-assistant.io/)
* [Homebridge](https://github.com/home-assistant/homebridge-homeassistant)
* [Plex](https://www.plex.tv/) media server in a Docker container using the command
```
docker create \
--name plex --net=host --restart=always \
-e TZ="America/New York" \
-e PUID=1000 -e PGID=1000 \
-e PLEX_CLAIM="<CLAIM>" \
-p 32400:32400 \
-v /docker/containers/plex/config:/config \
-v /docker/containers/plex/transcode:/transcode \
-v /mnt/music:/data/music:shared \
-v "/mnt/media/TV Shows":/data/tvshows:shared \
-v /mnt/bollywood:/data/bollywood:shared \
-v /mnt/hollywood:/data/movies:shared \
 plexinc/pms-docker:plexpass
 ```
* [Machinebox](https://machinebox.io/) image tagging service in a Docker container using the following command. First obtain your [API key](https://machinebox.io/login) and assign it to `MB_KEY` and then run the container using (you can access the Tagbox interface at http://ip.ad.dr.es:8081):
 ```
 $ sudo docker run --name=machinebox -p 8081:8080 -e "MB_KEY=$MB_KEY" -d machinebox/tagbox
 ```

## Some of the devices and services that I use with HA
  * [Aeotec Z-Stick Gen5](https://www.amazon.com/dp/B00X0AWA6E/) for Z-Wave control
    * I use a [z-wave dry contact relay](https://www.amazon.com/gp/product/B00ER6MH22/) along with a tilt sensor for automating my garage door.
    <img src="https://github.com/arsaboo/homeassistant-config/blob/master/z-wave_relay.png" alt="Z-wave Relay wiring" />
  * [Xiaomi Aqara](https://www.aliexpress.com/item/Original-Xiaomi-Smart-Gateway-2-Intelligent-Web-Wifi-Radio-and-Ringbell-Smart-Window-and-Door-Sensor/32816289388.html) for Zigbee sensors
    * Currently using [water](https://www.gearbest.com/home-smart-improvements/pp_668897.html), [temperature/humidity](https://www.gearbest.com/access-control/pp_626702.html), [door/window](https://www.gearbest.com/smart-light-bulb/pp_257677.html), and [human body](https://www.gearbest.com/alarm-systems/pp_659226.html) sensors
    * Also, using [Mi Magic Cube](https://www.aliexpress.com/item/Xiaomi-Mi-Magic-Cube-Controller-Zigbee-Version-Controlled-by-Six-Actions-For-Smart-Home-Device-work/32826737195.html) for volume and brightness automation.
  * Presence detection is the cornerstone for my setup and I use an elaborate approach as explained  [here](https://community.home-assistant.io/t/presence-detection-with-multiple-devices-multiple-trackers/4335). Currently, I combine the information from the following device trackers using a `python_script` and a Bayesian binary sensor. Here are the components that I use for presence:
    * [Unifi WAP](https://home-assistant.io/components/device_tracker.unifi/) for network-based device tracking
    * [OwnTracks](https://home-assistant.io/components/device_tracker.owntracks/),  [Geofency](https://home-assistant.io/components/device_tracker.geofency/), and Life360  [custom_component](/custom_components/sensor/life360.py) for tracking our iOS devices
    * [iOS app](https://itunes.apple.com/us/app/home-assistant-companion/id1099568401?mt=8)
  * Security
    * [Abode home security](https://home-assistant.io/components/alarm_control_panel.abode/) that is almost entirely automated using presence
    * Four [Hikvision DS-2CD2042WD-I](https://www.amazon.com/dp/B01M4MJECD/) cameras across the house integrated using [Synology Camera](https://home-assistant.io/components/camera.synology/) component
    * Three [Arlo cameras](https://home-assistant.io/components/arlo/) for indoor monitoring
    * [Ring](https://home-assistant.io/components/ring/) doorbell
  * Networking
    * [Ubiquiti Unifi Cloud Key](https://www.amazon.com/dp/B017T2QB22/)
    * [Ubiquiti Unifi 802.11ac PRO AP](https://www.amazon.com/dp/B015PRO512/)
    * [Pi-Hole](https://pi-hole.net/) with [Sensor](https://home-assistant.io/components/sensor.pi_hole/)
  * Lights and Switches
    * [LIFX wifi lights](https://www.amazon.com/dp/B01KY02MPG/)
    * [Wemo switches](https://www.amazon.com/dp/B00DGEGJ02/) for porch and driveway
    * [Wemo plugs](https://www.amazon.com/dp/B01DBXNYCS/) for miscellaneous automation including smart charging (to prevent overcharging), humidifier, Christmas lights, etc.
    * [GE Z-wave dimmer 12724](https://www.amazon.com/gp/product/B006LQFHN2/) for kitchen lights
  * Voice Interaction    
    * [Google Home](https://store.google.com/product/google_home), with the [Google Assistant](https://home-assistant.io/components/google_assistant/) and [Dialogflow](https://home-assistant.io/components/dialogflow/) components
    * [Amazon Echo Dot](https://www.amazon.com/dp/B01DFKC2SO/) with [HA Cloud](https://home-assistant.io/components/cloud/)
  * Media
    * [Sonos](https://www.sonos.com/) speakers and [component](https://home-assistant.io/components/media_player.sonos/)
    * [Plex](https://www.plex.tv/) for media consumption along with [Plex component](https://home-assistant.io/components/media_player.plex/)
    * [Plex activity monitor](https://home-assistant.io/components/sensor.plex/) to track my PMS.
    * [Google Cast](https://home-assistant.io/components/media_player.cast/) on my Nvidia Shield TV
  * Notifications:
    * [iOS ](https://home-assistant.io/docs/ecosystem/ios/notifications/basic/) and [Pushbullet](https://home-assistant.io/components/notify.pushbullet/) for basic notifications
    * [Telegram](https://home-assistant.io/components/notify.telegram/) and iOS for [actionable notifications](https://home-assistant.io/docs/ecosystem/ios/notifications/actions/)
    * [TTS](https://home-assistant.io/components/tts/) with the Sonos
    * [Notification for Android TV](https://home-assistant.io/components/notify.nfandroidtv/) to send visual notifications to Shield
  * Weather and Climate related
    * [Ecobee](https://home-assistant.io/components/ecobee/) thermostats in the main floor and kids rooms
    * [Wunderground](https://home-assistant.io/components/sensor.wunderground/) to integrate my weather station
    * [Bloomsky](https://home-assistant.io/components/bloomsky/) weather station
    [DarkSky](https://darksky.net/dev/) for weather data and forecasts
    * [Yahoo Weather](https://home-assistant.io/components/weather.yweather/) for weather card
    * [Pollen](https://home-assistant.io/components/sensor.pollen/) sensor for allergy related information

## My Home Assistant dashboard

I moved my entire configuration to Lovelace. Here are some screenshots (please note that these may not be the most updated images, but you should get an idea).
<img src="https://github.com/arsaboo/homeassistant-config/blob/master/ha_ss_1.png" alt="Home Assistant dashboard" />

<img src="https://github.com/arsaboo/homeassistant-config/blob/master/ha_ss_2.png" alt="Home Assistant dashboard" />

<img src="https://github.com/arsaboo/homeassistant-config/blob/master/ha_ss_3.png" alt="Home Assistant dashboard" />

<img src="https://github.com/arsaboo/homeassistant-config/blob/master/ha_ss_4.png" alt="Home Assistant dashboard" />

<img src="https://github.com/arsaboo/homeassistant-config/blob/master/ha_ss_5.png" alt="Home Assistant dashboard" />

# Useful links

* [HA cheat sheet](/HASS%20Cheatsheet.md) for miscellaneous tips and tricks.
