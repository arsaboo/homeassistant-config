# GE Dimmer Switch Connected to SmartThings via MQTT
# Python script to turn it on over a period of X minutes
entity_id  = data.get('entity_id')
sleep_delay = int(data.get('delay_in_sec'))
start_level_pct = int(data.get('start_level_pct'))
end_level_pct = int(data.get('end_level_pct'))
step_pct  = int(data.get('step_in_level_pct'))

start_level = int(255*start_level_pct/100)
end_level = int(255*end_level_pct/100)
step = int(255*step_pct/100)

new_level = start_level
while new_level < end_level
	states = hass.states.get(entity_id)
	current_level = states.attributes.get('brightness') or 0
	if (current_level > new_level) :
		logger.info('Exiting Fade In')
		break;
	else :
		logger.info('Setting brightness of ' + str(entity_id) + ' from ' + current_level + ' to ' + new_level)
		data = { "entity_id" : entity_id, "brightness" : new_level }
		hass.services.call('light', 'turn_on', data)
		new_level = new_level + step
		time.sleep(sleep_delay)
