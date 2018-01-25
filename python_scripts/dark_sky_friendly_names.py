###############################################################################
# Author:      Alok R. Saboo
# Description:  This script takes the dark_sky forecast sensors and updates
#               their friendly_name to include the date and day.
#               https://github.com/arsaboo/homeassistant-config/blob/master/packages/weather.yaml
###############################################################################
dark_sky_entities = ["sensor.forecast_1", "sensor.forecast_2", "sensor.forecast_3",
                     "sensor.forecast_4", "sensor.forecast_5", "sensor.forecast_6",
                     "sensor.forecast_7"]
days = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]

now = datetime.datetime.now()

tsToday = datetime.datetime(now.year, now.month, now.day, now.hour, now.minute, now.second, now.microsecond)
today = tsToday.weekday()
day = datetime.timedelta(days=1)
tomorrow = now + day
dt7 = datetime.datetime(tomorrow.year, tomorrow.month, tomorrow.day, tomorrow.hour, tomorrow.minute, tomorrow.second, tomorrow.microsecond)
logger.info("Tomorrow is {}".format(days[dt7.weekday()]))


for entity_id in dark_sky_entities:
    # copy it's state
    state = hass.states.get(entity_id)
    newState = state.state
    forecastdays = int(entity_id.split('_')[1])
    day = datetime.timedelta(days = forecastdays)
    forecastdate = now + day
    logger.info("NewState {} ({}/{})".format(state.state, forecastdate.month, forecastdate.day))
    newEntityPicture = state.attributes.get('entity_picture')
    if today + forecastdays > 6:
        newDay = days[today + forecastdays - 7]
    else:
        newDay = days[today + forecastdays]
    logger.info("Tomorrow is {}".format(newDay))
    # Set states
    hass.states.set(entity_id, newState, {
        'friendly_name': "{} ({}/{})".format(newDay, forecastdate.month, forecastdate.day),
        'entity_picture': newEntityPicture,
    })
