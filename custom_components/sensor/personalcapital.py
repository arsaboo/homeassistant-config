"""
Support for Personal Capital sensors.

For more details about this platform, please refer to the documentation at
https://github.com/custom-components/sensor.personalcapital
"""

import logging
import voluptuous as vol
import json
from datetime import timedelta
from homeassistant.helpers.entity import Entity
import homeassistant.helpers.config_validation as cv
from homeassistant.components.sensor import (PLATFORM_SCHEMA)
from homeassistant.util import Throttle

__version__ = '0.0.5'

REQUIREMENTS = ['personalcapital==1.0.1']

CONF_EMAIL = 'email'
CONF_PASSWORD = 'password'
CONF_UNIT_OF_MEASUREMENT = 'unit_of_measurement'
CONF_CATEGORIES = 'monitored_categories'

SESSION_FILE = '.pc-session'
DATA_PERSONAL_CAPITAL = 'personalcapital_cache'

ATTR_NETWORTH = 'networth'
ATTR_ASSETS = 'assets'
ATTR_LIABILITIES = 'liabilities'
ATTR_INVESTMENTS = 'investments'
ATTR_MORTGAGES = 'mortgages'
ATTR_CASH = 'cash'
ATTR_OTHER_ASSETS = 'other_assets'
ATTR_OTHER_LIABILITIES = 'other_liabilities'
ATTR_CREDIT = 'credit_cards'
ATTR_LOANS = 'loans'

SCAN_INTERVAL = timedelta(minutes=15)
MIN_TIME_BETWEEN_UPDATES = timedelta(minutes=30)

SENSOR_TYPES = {
    ATTR_NETWORTH: None,
    ATTR_ASSETS: ['BANK', '', 'assets', 'Assets'],
    ATTR_LIABILITIES: ['LIABILITIES', '', 'liabilities', 'Liabilities'],
    ATTR_INVESTMENTS: ['INVESTMENT', '', 'investmentAccountsTotal', 'Investments'],
    ATTR_MORTGAGES: ['MORTGAGE', '', 'mortgageAccountsTotal', 'Mortgages'],
    ATTR_CASH: ['BANK', 'Cash', 'cashAccountsTotal', 'Cash'],
    ATTR_OTHER_ASSETS: ['OTHER_ASSETS', '', 'otherAssetAccountsTotal', 'Other Assets'],
    ATTR_OTHER_LIABILITIES: ['OTHER_LIABILITIES', '', 'otherLiabilitiesAccountsTotal', 'Other Liabilities'],
    ATTR_CREDIT: ['CREDIT_CARD', '', 'creditCardAccountsTotal', 'Credit'],
    ATTR_LOANS: ['LOAN', '', 'loanAccountsTotal', 'Loans'],
}

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_EMAIL): cv.string,
    vol.Required(CONF_PASSWORD): cv.string,
    vol.Optional(CONF_UNIT_OF_MEASUREMENT, default='USD'): cv.string,
    vol.Optional(CONF_CATEGORIES, default=[]): vol.All(cv.ensure_list, [vol.In(SENSOR_TYPES)]),
})

_CONFIGURING = {}
_LOGGER = logging.getLogger(__name__)


def request_app_setup(hass, config, pc, add_devices, discovery_info=None):
    """Request configuration steps from the user."""
    from personalcapital import PersonalCapital, RequireTwoFactorException, TwoFactorVerificationModeEnum
    configurator = hass.components.configurator

    def personalcapital_configuration_callback(data):
        """Run when the configuration callback is called."""
        from personalcapital import PersonalCapital, RequireTwoFactorException, TwoFactorVerificationModeEnum
        pc.two_factor_authenticate(TwoFactorVerificationModeEnum.SMS, data.get('verification_code'))
        result = pc.authenticate_password(config.get(CONF_PASSWORD))

        if result == RequireTwoFactorException:
            configurator.notify_errors(_CONFIGURING['personalcapital'], "Invalid verification code")
        else:
            save_session(hass, pc.get_session())
            continue_setup_platform(hass, config, pc, add_devices, discovery_info)

    if 'personalcapital' not in _CONFIGURING:
        try:
            pc.login(config.get(CONF_EMAIL), config.get(CONF_PASSWORD))
        except RequireTwoFactorException:
            pc.two_factor_challenge(TwoFactorVerificationModeEnum.SMS)

    _CONFIGURING['personalcapital'] = configurator.request_config(
        'Personal Capital',
        personalcapital_configuration_callback,
        description="Verification code sent to phone",
        submit_caption='Verify',
        fields=[{
            'id': 'verification_code',
            'name': "Verification code",
            'type': 'string'}]
    )


def load_session(hass):
    try:
        with open(hass.config.path(SESSION_FILE)) as data_file:
            cookies = {}
            try:
                cookies = json.load(data_file)
            except ValueError as err:
                return {}
            return cookies
    except IOError as err:
        return {}


def save_session(hass, session):
    with open(hass.config.path(SESSION_FILE), 'w') as data_file:
        data_file.write(json.dumps(session))


def setup_platform(hass, config, add_devices, discovery_info=None):
    """Set up the Personal Capital component."""
    from personalcapital import PersonalCapital, RequireTwoFactorException, TwoFactorVerificationModeEnum
    pc = PersonalCapital()
    session = load_session(hass)

    if len(session) > 0:
        pc.set_session(session)

        try:
            pc.login(config.get(CONF_EMAIL), config.get(CONF_PASSWORD))
            continue_setup_platform(hass, config, pc, add_devices, discovery_info)
        except RequireTwoFactorException:
            request_app_setup(hass, config, pc, add_devices, discovery_info)
    else:
        request_app_setup(hass, config, pc, add_devices, discovery_info)


def continue_setup_platform(hass, config, pc, add_devices, discovery_info=None):
    """Set up the Personal Capital component."""
    if "personalcapital" in _CONFIGURING:
        hass.components.configurator.request_done(_CONFIGURING.pop("personalcapital"))

    rest_pc = PersonalCapitalAccountData(pc, config)
    uom = config[CONF_UNIT_OF_MEASUREMENT]
    sensors = []
    categories = config[CONF_CATEGORIES] if len(config[CONF_CATEGORIES]) > 0 else SENSOR_TYPES.keys()
    if ATTR_NETWORTH in categories:
        sensors.append(PersonalCapitalNetWorthSensor(rest_pc, config[CONF_UNIT_OF_MEASUREMENT], categories))
    for category in categories:
        if category != ATTR_NETWORTH:
            sensors.append(PersonalCapitalCategorySensor(hass, rest_pc, uom, category))
    add_devices(sensors, True)


class PersonalCapitalNetWorthSensor(Entity):
    """Representation of a personalcapital.com net worth sensor."""

    def __init__(self, rest, unit_of_measurement, categories):
        """Initialize the sensor."""
        self._rest = rest
        self._unit_of_measurement = unit_of_measurement
        self._categories = categories
        self._state = None
        self._networth = None
        self._assets = None
        self._liabilities = None
        self._investments = None
        self._mortgages = None
        self._cash = None
        self._other_assets = None
        self._other_liabilities = None
        self._credit = None
        self._loans = None
        self.update()

    def update(self):
        """Get the latest state of the sensor."""
        self._rest.update()
        data = self._rest.data.json()['spData']
        self._state = data.get('networth', 0.0)
        self._networth = data.get('networth', 0.0)
        self._assets = data.get('assets', 0.0)
        self._liabilities = data.get('liabilities', 0.0)
        self._investments = data.get('investmentAccountsTotal', 0.0)
        self._mortgages = data.get('mortgageAccountsTotal', 0.0)
        self._cash = data.get('cashAccountsTotal', 0.0)
        self._other_assets = data.get('otherAssetAccountsTotal', 0.0)
        self._other_liabilities = data.get('otherLiabilitiesAccountsTotal', 0.0)
        self._credit = data.get('creditCardAccountsTotal', 0.0)
        self._loans = data.get('loanAccountsTotal', 0.0)

    @property
    def name(self):
        """Return the name of the sensor."""
        return 'Personal Capital Networth'

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def unit_of_measurement(self):
        """Return the unit of measure this sensor expresses itself in."""
        return self._unit_of_measurement

    @property
    def icon(self):
        """Return the icon to use in the frontend."""
        return 'mdi:coin'

    @property
    def device_state_attributes(self):
        """Return the state attributes of the sensor."""
        attributes = {ATTR_NETWORTH: self._networth}
        if ATTR_ASSETS in self._categories:
            attributes[ATTR_ASSETS] = self._assets
        if ATTR_LIABILITIES in self._categories:
            attributes[ATTR_LIABILITIES] = self._liabilities
        if ATTR_INVESTMENTS in self._categories:
            attributes[ATTR_INVESTMENTS] = self._investments
        if ATTR_MORTGAGES in self._categories:
            attributes[ATTR_MORTGAGES] = self._mortgages
        if ATTR_CASH in self._categories:
            attributes[ATTR_CASH] = self._cash
        if ATTR_OTHER_ASSETS in self._categories:
            attributes[ATTR_OTHER_ASSETS] = self._other_assets
        if ATTR_OTHER_LIABILITIES in self._categories:
            attributes[ATTR_OTHER_LIABILITIES] = self._other_liabilities
        if ATTR_CREDIT in self._categories:
            attributes[ATTR_CREDIT] = self._credit
        if ATTR_LOANS in self._categories:
            attributes[ATTR_LOANS] = self._loans
        return attributes


class PersonalCapitalCategorySensor(Entity):
    """Representation of a personalcapital.com sensor."""

    def __init__(self, hass, rest, unit_of_measurement, sensor_type):
        """Initialize the sensor."""
        self.hass = hass
        self._rest = rest
        self._name = f'Personal Capital {SENSOR_TYPES[sensor_type][3]}'
        self._productType = SENSOR_TYPES[sensor_type][0]
        self._accountType = SENSOR_TYPES[sensor_type][1]
        self._balanceName = SENSOR_TYPES[sensor_type][2]
        self._state = None
        self._unit_of_measurement = unit_of_measurement
        self.hass.data[self._productType] = {}

    def update(self):
        """Get the latest state of the sensor."""
        self._rest.update()
        data = self._rest.data.json()['spData']
        self._state = data.get(self._balanceName, 0.0)
        accounts = data.get('accounts')

        for account in accounts:
            if self._productType == account.get('productType') and \
               (self._accountType == '' or self._accountType == account.get('accountType', '')) and \
               account.get('closeDate', '') == '':
                self.hass.data[self._productType][account.get('name', '')] = {
                    "name": account.get('name', ''),
                    "firm_name": account.get('firmName', ''),
                    "logo": account.get('logoPath', ''),
                    "balance": account.get('balance', 0.0),
                    "account_type": account.get('accountType', ''),
                    "url": account.get('homeUrl', ''),
                    "currency": account.get('currency', ''),
                }

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement this sensor expresses itself in."""
        return self._unit_of_measurement

    @property
    def icon(self):
        """Return the icon to use in the frontend."""
        return 'mdi:coin'

    @property
    def device_state_attributes(self):
        """Return the state attributes of the sensor."""
        return self.hass.data[self._productType]


class PersonalCapitalAccountData(object):
    """Get data from personalcapital.com"""

    def __init__(self, pc, config):
        self._pc = pc
        self.data = None
        self._config = config

    @Throttle(MIN_TIME_BETWEEN_UPDATES)
    def update(self):
        """Get latest data from personal capital"""
        self.data = self._pc.fetch('/newaccount/getAccounts')

        if not self.data or not self.data.json()['spHeader']['success']:
            self._pc.login(self._config[CONF_EMAIL], self._config[CONF_PASSWORD])
            self.data = self._pc.fetch('/newaccount/getAccounts')
