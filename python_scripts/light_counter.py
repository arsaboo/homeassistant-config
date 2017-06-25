on = 0
for entity_id in hass.states.entity_ids('light'):
    state = hass.states.get(entity_id)
    if state.state == 'on':
        on = on + 1
hass.states.set('sensor.lights_on', on, {
    'unit_of_measurement': 'lights',
    'friendly_name': 'Lights On'
})
