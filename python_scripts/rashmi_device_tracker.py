# Combine multiple device trackers into one entity
#
# OPTIONS
# New tracker name
metatrackerName = 'device_tracker.meta_rashmi'

# Get Data from Automation Trigger
triggeredEntity = data.get('entity_id')
# Get current & new state
newState = hass.states.get(triggeredEntity)
currentState = hass.states.get(metatrackerName)
# Get New data
newSource = newState.attributes.get('source_type')

# If GPS source, set new coordinates
if newSource == 'gps':
  newLatitude = newState.attributes.get('latitude')
  newLongitude = newState.attributes.get('longitude')
  newgpsAccuracy = newState.attributes.get('gps_accuracy')
# If not, keep last known coordinates
elif currentState.attributes.get('latitude') is not None:
  newLatitude = currentState.attributes.get('latitude')
  newLongitude = currentState.attributes.get('longitude')
  newgpsAccuracy = currentState.attributes.get('gps_accuracy')
# Otherwise return null
else:
  newLatitude = None
  newLongitude = None
  newgpsAccuracy = None

# Get Battery
if newState.attributes.get('battery') is not None:
  newBattery = newState.attributes.get('battery')
elif currentState.attributes.get('battery') is not None:
  newBattery = currentState.attributes.get('battery')
else:
  newBattery = None

# Set new state and icon
# Everything updates 'home'
if newState.state == 'home':
  newStatus = 'home'
  newIcon = 'mdi:home-map-marker'
# only GPS platforms update 'not_home'
elif newState.state == 'not_home':
    newStatus = 'not_home'
    newIcon = 'mdi:home'
# Otherwise keep old status
else:
    newStatus = currentState.state

# Create device_tracker.meta entity
hass.states.set(metatrackerName, newStatus, {
    'friendly_name': 'Rashmi Tracker',
    'icon': newIcon,
    'source_type': newSource,
    'battery': newBattery,
    'gps_accuracy': newgpsAccuracy,
    'latitude': newLatitude,
    'longitude': newLongitude,
    'last_update_source': triggeredEntity
})
