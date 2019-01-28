# Manually toggle state of a device_tracker entity
# You can call the script using the following:
# - service: python_script.toggle_state
#   data_template:
#     entity_id: '{{trigger.entity_id}}'

# Get the entity that triggered the automation
triggeredEntity = data.get('entity_id')
currentState = hass.states.get(triggeredEntity)

if currentState == 'home':
    newStatus = 'not_home'
else:
    newStatus = 'home'

hass.states.set(triggeredEntity, newStatus)
logger.warning("Set %s to %s",triggeredEntity, newStatus)
