AlokFriendlyName = 'Alok Test Tracker'
AlokEntityPicture = '/local/icons/Alok.png'
AloktrackerName = 'device_tracker.test_alok'

RashmiFriendlyName = 'Rashmi Test Tracker'
RashmiEntityPicture = '/local/icons/Rashmi.png'
RashmitrackerName = 'device_tracker.test_rashmi'

AlokcurrentState = hass.states.get(AloktrackerName)
AloknewStatus = AlokcurrentState.state

RashmicurrentState = hass.states.get(RashmitrackerName)
RashminewStatus = RashmicurrentState.state

# Create device_tracker.test_alok entity
hass.states.set(AloktrackerName, AloknewStatus, {
    'friendly_name': AlokFriendlyName,
    'entity_picture': AlokEntityPicture,
    'show_last_changed': 'true'
})

# Create device_tracker.test_rashmi entity
hass.states.set(RashmitrackerName, RashminewStatus, {
    'friendly_name': RashmiFriendlyName,
    'entity_picture': RashmiEntityPicture,
    'show_last_changed': 'true'
})
