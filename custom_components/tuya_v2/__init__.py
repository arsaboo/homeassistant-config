"""Support for Tuya Smart devices."""

import itertools
from typing import Any
import logging
import json

import voluptuous as vol

from tuya_iot import (
    ProjectType,
    TuyaDevice,
    TuyaDeviceListener,
    TuyaDeviceManager,
    TuyaHomeManager,
    TuyaOpenAPI,
    TuyaOpenMQ,
    tuya_logger
)

from .aes_cbc import AES_ACCOUNT_KEY, KEY_KEY, XOR_KEY
from .aes_cbc import AesCBC as Aes

import homeassistant.helpers.config_validation as cv
from homeassistant.config_entries import ConfigEntry, SOURCE_IMPORT
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import device_registry
from homeassistant.helpers.dispatcher import dispatcher_send
from homeassistant.data_entry_flow import UnknownFlow, UnknownStep

from .const import (
    CONF_ACCESS_ID,
    CONF_ACCESS_SECRET,
    CONF_APP_TYPE,
    CONF_COUNTRY_CODE,
    CONF_ENDPOINT,
    CONF_PASSWORD,
    CONF_PROJECT_TYPE,
    CONF_USERNAME,
    DOMAIN,
    PLATFORMS,
    TUYA_DEVICE_MANAGER,
    TUYA_DISCOVERY_NEW,
    TUYA_HA_DEVICES,
    TUYA_HA_SIGNAL_UPDATE_ENTITY,
    TUYA_HA_TUYA_MAP,
    TUYA_HOME_MANAGER,
    TUYA_MQTT_LISTENER,
)

_LOGGER = logging.getLogger(__name__)

CONFIG_SCHEMA = vol.Schema(
    vol.All(
        cv.deprecated(DOMAIN),
        {
            DOMAIN: vol.Schema(
                {
                    vol.Required(CONF_PROJECT_TYPE): int,
                    vol.Required(CONF_ENDPOINT): cv.string,
                    vol.Required(CONF_ACCESS_ID): cv.string,
                    vol.Required(CONF_ACCESS_SECRET): cv.string,
                    CONF_USERNAME: cv.string,
                    CONF_PASSWORD: cv.string,
                    CONF_COUNTRY_CODE: cv.string,
                    CONF_APP_TYPE: cv.string,
                }
            )
        },
    ),
    extra=vol.ALLOW_EXTRA,
)

def entry_decrypt(hass: HomeAssistant, entry: ConfigEntry, init_entry_data):
    """Decript or encrypt entry info."""
    aes = Aes()
    # decrypt the new account info
    if XOR_KEY in init_entry_data:
        _LOGGER.info("tuya.__init__.exist_xor_cache-->True")
        key_iv = aes.xor_decrypt(init_entry_data[XOR_KEY], init_entry_data[KEY_KEY])
        cbc_key = key_iv[0:16]
        cbc_iv = key_iv[16:32]
        decrpyt_str = aes.cbc_decrypt(cbc_key, cbc_iv, init_entry_data[AES_ACCOUNT_KEY])
        # _LOGGER.info(f"tuya.__init__.exist_xor_cache:::decrpyt_str-->{decrpyt_str}")
        entry_data = aes.json_to_dict(decrpyt_str)
    else:
        # if not exist xor cache, use old account info
        _LOGGER.info("tuya.__init__.exist_xor_cache-->False")
        entry_data = init_entry_data
        cbc_key = aes.random_16()
        cbc_iv = aes.random_16()
        access_id = init_entry_data[CONF_ACCESS_ID]
        access_id_entry = aes.cbc_encrypt(cbc_key, cbc_iv, access_id)
        c = cbc_key + cbc_iv
        c_xor_entry = aes.xor_encrypt(c, access_id_entry)
        # account info encrypted with AES-CBC
        user_input_encrpt = aes.cbc_encrypt(
            cbc_key, cbc_iv, json.dumps(dict(init_entry_data))
        )
        # udpate old account info
        hass.config_entries.async_update_entry(
            entry,
            data={
                AES_ACCOUNT_KEY: user_input_encrpt,
                XOR_KEY: c_xor_entry,
                KEY_KEY: access_id_entry,
            },
        )
    return entry_data

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Async setup hass config entry."""

    _LOGGER.debug("tuya.__init__.async_setup_entry-->%s", entry.data)

    hass.data[DOMAIN] = {entry.entry_id: {TUYA_HA_TUYA_MAP: {}, TUYA_HA_DEVICES: set()}}

    success = await _init_tuya_sdk(hass, entry)
    if not success:
        return False

    return True


async def _init_tuya_sdk(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    entry_data = entry_decrypt(hass, entry, entry.data)
    project_type = ProjectType(entry_data[CONF_PROJECT_TYPE])

    api = TuyaOpenAPI(
        entry_data[CONF_ENDPOINT],
        entry_data[CONF_ACCESS_ID],
        entry_data[CONF_ACCESS_SECRET],
        project_type,
    )

    api.set_dev_channel("hass")

    if project_type == ProjectType.INDUSTY_SOLUTIONS:
        response = await hass.async_add_executor_job(
            api.login, entry_data[CONF_USERNAME], entry_data[CONF_PASSWORD]
        )
    else:
        response = await hass.async_add_executor_job(
            api.login,
            entry_data[CONF_USERNAME],
            entry_data[CONF_PASSWORD],
            entry_data[CONF_COUNTRY_CODE],
            entry_data[CONF_APP_TYPE],

        )

    if response.get("success", False) is False:
        _LOGGER.error("Tuya login error response: %s", response)
        return False

    tuya_mq = TuyaOpenMQ(api)
    tuya_mq.start()

    device_manager = TuyaDeviceManager(api, tuya_mq)

    # Get device list
    home_manager = TuyaHomeManager(api, tuya_mq, device_manager)
    await hass.async_add_executor_job(home_manager.update_device_cache)
    hass.data[DOMAIN][entry.entry_id][TUYA_HOME_MANAGER] = home_manager

    listener = DeviceListener(hass, entry)
    hass.data[DOMAIN][entry.entry_id][TUYA_MQTT_LISTENER] = listener
    device_manager.add_device_listener(listener)
    hass.data[DOMAIN][entry.entry_id][TUYA_DEVICE_MANAGER] = device_manager

    # Clean up device entities
    await cleanup_device_registry(hass, entry)

    _LOGGER.debug("init support type->%s", PLATFORMS)

    hass.config_entries.async_setup_platforms(entry, PLATFORMS)

    return True


async def cleanup_device_registry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Remove deleted device registry entry if there are no remaining entities."""

    device_registry_object = device_registry.async_get(hass)
    device_manager = hass.data[DOMAIN][entry.entry_id][TUYA_DEVICE_MANAGER]

    for dev_id, device_entry in list(device_registry_object.devices.items()):
        for item in device_entry.identifiers:
            if DOMAIN == item[0] and item[1] not in device_manager.device_map:
                device_registry_object.async_remove_device(dev_id)
                break


@callback
def async_remove_hass_device(hass: HomeAssistant, device_id: str) -> None:
    """Remove device from hass cache."""
    device_registry_object = device_registry.async_get(hass)
    for device_entry in list(device_registry_object.devices.values()):
        if device_id in list(device_entry.identifiers)[0]:
            device_registry_object.async_remove_device(device_entry.id)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unloading the Tuya platforms."""
    _LOGGER.debug("integration unload")
    unload = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload:
        device_manager = hass.data[DOMAIN][entry.entry_id][TUYA_DEVICE_MANAGER]
        device_manager.mq.stop()
        device_manager.remove_device_listener(
            hass.data[DOMAIN][entry.entry_id][TUYA_MQTT_LISTENER]
        )

        hass.data.pop(DOMAIN)

    return unload

async def async_setup(hass: HomeAssistant, config):
    """Set up the Tuya integration."""
    tuya_logger.setLevel(_LOGGER.level)
    conf = config.get(DOMAIN)

    _LOGGER.debug(f"Tuya async setup conf {conf}")
    if conf is not None:

        async def flow_init() -> Any:
            try:
                result = await hass.config_entries.flow.async_init(
                    DOMAIN, context={"source": SOURCE_IMPORT}, data=conf
                )
            except UnknownFlow as flow:
                _LOGGER.error(flow.args)
            except UnknownStep as step:
                _LOGGER.error(step.args)
            except ValueError as err:
                _LOGGER.error(err.args)
            _LOGGER.info("Tuya async setup flow_init")
            return result

        hass.async_create_task(flow_init())

    return True



class DeviceListener(TuyaDeviceListener):
    """Device Update Listener."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Init DeviceListener."""

        self.hass = hass
        self.entry = entry

    def update_device(self, device: TuyaDevice) -> None:
        """Update device status."""
        if device.id in self.hass.data[DOMAIN][self.entry.entry_id][TUYA_HA_DEVICES]:
            _LOGGER.debug(
                "_update-->%s;->>%s",
                self,
                device.id,
            )
            dispatcher_send(self.hass, f"{TUYA_HA_SIGNAL_UPDATE_ENTITY}_{device.id}")

    def add_device(self, device: TuyaDevice) -> None:
        """Add device added listener."""
        device_add = False

        if device.category in itertools.chain(
            *self.hass.data[DOMAIN][self.entry.entry_id][TUYA_HA_TUYA_MAP].values()
        ):
            ha_tuya_map = self.hass.data[DOMAIN][self.entry.entry_id][TUYA_HA_TUYA_MAP]
            self.hass.add_job(async_remove_hass_device, self.hass, device.id)

            for domain, tuya_list in ha_tuya_map.items():
                if device.category in tuya_list:
                    device_add = True
                    _LOGGER.debug(
                        "Add device category->%s; domain-> %s",
                        device.category,
                        domain,
                    )
                    self.hass.data[DOMAIN][self.entry.entry_id][TUYA_HA_DEVICES].add(
                        device.id
                    )
                    dispatcher_send(
                        self.hass, TUYA_DISCOVERY_NEW.format(domain), [device.id]
                    )

        if device_add:
            device_manager = self.hass.data[DOMAIN][self.entry.entry_id][
                TUYA_DEVICE_MANAGER
            ]
            device_manager.mq.stop()
            tuya_mq = TuyaOpenMQ(device_manager.api)
            tuya_mq.start()

            device_manager.mq = tuya_mq
            tuya_mq.add_message_listener(device_manager.on_message)

    def remove_device(self, device_id: str) -> None:
        """Add device removed listener."""
        _LOGGER.debug("tuya remove device:%s", device_id)
        self.hass.add_job(async_remove_hass_device, self.hass, device_id)
