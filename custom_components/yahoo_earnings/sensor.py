"""
@ Author      : Alok Saboo
@ Description : Earnings Estimates from Yahoo Finance
"""

import json
import pytz
import requests
import urllib3
import logging

import voluptuous as vol
from datetime import datetime, timedelta, date
from lxml import html


import homeassistant.helpers.config_validation as cv
from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.const import (CONF_NAME, ATTR_ATTRIBUTION)
from homeassistant.helpers.entity import Entity
from homeassistant.util import Throttle

_LOGGER = logging.getLogger(__name__)

ATTRIBUTION = "Data provided by Yahoo.com"
DEFAULT_ICON = 'mdi:currency-usd'

SCAN_INTERVAL = timedelta(hours=24)
MIN_TIME_BETWEEN_UPDATES = timedelta(hours=24)

CONF_TICKER = 'ticker'
DEFAULT_NAME = 'yahoo earnings'

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_TICKER): cv.string,
        vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
    }
)

def setup_platform(hass, config, add_devices, discovery_info=None):
    """Set up the Yahoo earnings sensor."""
    ticker = config.get(CONF_TICKER)
    if not ticker:
        msg = "Warning: No Tickers configured."
        hass.components.persistent_notification.create(msg, "Sensor yahoo_earnings")
        _LOGGER.warning(msg)
        return
    rest = YahooEarningsData(ticker)
    name = config.get(CONF_NAME)
    add_devices([YahooEarningsSensor(name, rest)], True)


class YahooEarningsSensor(Entity):
    """Implementing the Yahoo earnings sensor."""

    def __init__(self, name, rest):
        """Initialize the sensor."""
        self._icon = DEFAULT_ICON
        self.rest = rest
        self._state = None
        self._name = name

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name.rstrip()

    @property
    def icon(self):
        """Return the icon to use in the frontend, if any."""
        icon = DEFAULT_ICON
        return icon

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def device_state_attributes(self):
        """Return the state attributes of the sensor."""
        attr = {}
        attr['history'] = self.format_history(self.rest.data['History'])
        attr['Ticker'] = self.rest.data['Ticker']
        attr['Mean Target'] = self.rest.data['Mean Target']
        attr['Median Target'] = self.rest.data['Median Target']
        attr['Recommendation Mean'] = self.rest.data['Recommendation Mean']
        attr['Recommendation'] = self.rest.data['Recommendation']
        attr['Number of Analysts'] = self.rest.data['Number of Analysts']
        attr['Insider Ownership'] = self.rest.data['Insider Ownership']
        attr['Institutional Ownership'] = self.rest.data['Institutional Ownership']
        attr[ATTR_ATTRIBUTION] = ATTRIBUTION
        return attr

    @property
    def available(self):
        """Could the device be accessed during the last update call."""
        return self.rest.available

    def update(self):
        """Update current date."""
        self.rest.update()
        self._state = float(self.rest.data['Recommendation Mean'])

    def format_history(self, history):
        edited = []
        for entry in history:
            edit = entry.copy()
            edit["epochGradeDate"] = datetime.fromtimestamp(edit["epochGradeDate"], pytz.timezone("UTC")).strftime('%Y-%m-%d')
            if edit["action"] == "up":
                edit["action"] = "Upgraded"
            elif edit["action"] == "init":
                edit["action"] = "Initiated"
            elif edit["action"] == "down":
                edit["action"] = "Downgraded"
            elif edit["action"] == "main":
                edit["action"] = "Maintained"
            edited.append(edit)
        return edited

class YahooEarningsData(object):
    """Get data from yahoo.com."""

    def __init__(self, ticker):
        """Initialize the data object."""
        self._ticker = ticker
        self.data = None
        self.available = True

    @Throttle(MIN_TIME_BETWEEN_UPDATES)
    def update(self):
        """Get the latest data from CNN."""
        from random_user_agent.user_agent import UserAgent
        from random_user_agent.params import SoftwareName, OperatingSystem

        software_names = [SoftwareName.CHROME.value]
        operating_systems = [OperatingSystem.WINDOWS.value, OperatingSystem.LINUX.value]

        user_agent_rotator = UserAgent(software_names=software_names, operating_systems=operating_systems, limit=100)

        # Get list of user agents.
        user_agent = user_agent_rotator.get_random_user_agent()

        headers = {'User-Agent': user_agent}

        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        other_details_json_link = "https://query2.finance.yahoo.com/v10/finance/quoteSummary/{0}?formatted=true&lang=en-US&region=US&modules=summaryProfile%2CfinancialData%2CrecommendationTrend%2CupgradeDowngradeHistory%2Cearnings%2CdefaultKeyStatistics%2CcalendarEvents&corsDomain=finance.yahoo.com".format(self._ticker)
        try:
            summary_json_response = requests.get(other_details_json_link, verify=False, headers=headers, timeout=10)
            _LOGGER.debug("Yahoo earnings updated")
            json_loaded_summary =  json.loads(summary_json_response.text)
            quotes_json = json_loaded_summary["quoteSummary"]["result"][0]
            upgradeDowngradeHistory = quotes_json["upgradeDowngradeHistory"]['history']
            recommendationMean = quotes_json["financialData"]["recommendationMean"]['raw']
            targetMeanPrice = quotes_json["financialData"]["targetMeanPrice"]['raw']
            targetMedianPrice = quotes_json["financialData"]["targetMedianPrice"]['raw']
            recommendationKey = quotes_json["financialData"]["recommendationKey"]
            numberOfAnalystOpinions = quotes_json["financialData"]["numberOfAnalystOpinions"]['raw']
            heldPercentInsiders = quotes_json["defaultKeyStatistics"]["heldPercentInsiders"]["raw"]
            heldPercentInstitutions = quotes_json["defaultKeyStatistics"]["heldPercentInstitutions"]["raw"]

            results_json = {}
            results_json['Ticker'] = self._ticker
            results_json['Mean Target'] = targetMeanPrice
            results_json['Median Target'] = targetMedianPrice
            results_json['Recommendation Mean'] = recommendationMean
            results_json['Recommendation'] = recommendationKey
            results_json['Number of Analysts'] = numberOfAnalystOpinions
            results_json['Insider Ownership'] = heldPercentInsiders
            results_json['Institutional Ownership'] = heldPercentInstitutions
            results_json['History'] = upgradeDowngradeHistory
            self.data = results_json
            self.available = True
        except requests.exceptions.ConnectionError:
            _LOGGER.error("Connection error")
            self.data = None
            self.available = False
