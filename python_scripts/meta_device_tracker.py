# Combine multiple device trackers into one entity
# You can call the script using the following:
# - service: python_script.meta_device_tracker
#   data_template:
#     entity_id: '{{trigger.entity_id}}'
#     tracker: device_tracker.meta_alok

# OPTIONS
# Get the name of the tracker to be updated
metatrackerName = data.get('tracker')
# Get the entity that triggered the automation
triggeredEntity = data.get('entity_id')
# Get current & new state
newState = hass.states.get(triggeredEntity)
currentState = hass.states.get(metatrackerName)
# Get New data
newSource = newState.attributes.get('source_type')
newFriendlyName_temp = newState.attributes.get('friendly_name')

# If Rashmi in friendly_name, set friendly_name as Rashmi Tracker
if "Rashmi" not in newFriendlyName_temp:
    newFriendlyName = 'Alok Tracker'
else:
    newFriendlyName = 'Rashmi Tracker'

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

if newState.state is not None:
  newStatus = newState.state
else:
    newStatus = currentState.state

# Create device_tracker.meta entity
hass.states.set(metatrackerName, newStatus, {
    'friendly_name': newFriendlyName,
    'source_type': newSource,
    'battery': newBattery,
    'gps_accuracy': newgpsAccuracy,
    'latitude': newLatitude,
    'longitude': newLongitude,
    'update_source': triggeredEntity
})
