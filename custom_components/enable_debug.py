"""
Support for enabling debug mode in HASS.

Just add the following to yoru configuration.yaml
enable_debug:
"""
DOMAIN = 'enable_debug'

async def async_setup(hass, config):
    hass.loop.set_debug(True)
    return True
