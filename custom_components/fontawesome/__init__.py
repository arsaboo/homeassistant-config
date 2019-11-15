import homeassistant.components.frontend
from homeassistant.components.frontend import _frontend_root

from .custom_component_server import setup_view

DOMAIN = "fontawesome"

DATA_EXTRA_MODULE_URL = 'frontend_extra_module_url'
ICONS_URL = '/'+DOMAIN+'/data/'
ICON_FILES = {
    'regular': 'far.js',
    'solid': 'fas.js',
    'brands': 'fab.js',
}

async def async_setup(hass, config):
    setup_view(hass, DOMAIN)
    conf = config.get(DOMAIN)
    if not conf:
        return True
    register_modules(hass, conf)
    return True

async def async_setup_entry(hass, config_entry):
    config_entry.add_update_listener(_update_listener)
    register_modules(hass, config_entry.options)
    return True

async def async_remove_entry(hass, config_entry):
    register_modules(hass, [])
    return True

async def _update_listener(hass, config_entry):
    register_modules(hass, config_entry.options)
    return True


def register_modules(hass, modules):
    if DATA_EXTRA_MODULE_URL not in hass.data:
        hass.data[DATA_EXTRA_MODULE_URL] = set()
    url_set = hass.data[DATA_EXTRA_MODULE_URL]

    for k,v in ICON_FILES.items():
        url_set.discard(ICONS_URL+v)
        if k in modules and modules[k] != False:
            url_set.add(ICONS_URL+v)