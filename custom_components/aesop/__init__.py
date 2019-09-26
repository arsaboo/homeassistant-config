"""Support for Aesop data."""
from datetime import timedelta
import logging

import voluptuous as vol

from homeassistant.const import CONF_NAME, CONF_USERNAME, CONF_PASSWORD
from homeassistant.helpers import config_validation as cv, discovery
from homeassistant.util import Throttle
from homeassistant.util.dt import now

_LOGGER = logging.getLogger(__name__)

DOMAIN = "aesop"
DATA_AESOP = "data_aesop"
MIN_TIME_BETWEEN_UPDATES = timedelta(minutes=30)
COOKIE = "aesop_cookies.pickle"
CACHE = "aesop_cache"
CONF_DRIVER = "driver"

AESOP_TYPE = ["sensor"]

CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN: vol.Schema(
            {
                vol.Required(CONF_USERNAME): cv.string,
                vol.Required(CONF_PASSWORD): cv.string,
                vol.Optional(CONF_NAME, default=DOMAIN): cv.string,
                vol.Optional(CONF_DRIVER): cv.string,
            }
        )
    },
    extra=vol.ALLOW_EXTRA,
)


def setup(hass, config):
    """Use config values to set up a function enabling status retrieval."""

    conf = config[DOMAIN]
    username = conf.get(CONF_USERNAME)
    password = conf.get(CONF_PASSWORD)
    name = conf.get(CONF_NAME)
    driver = conf.get(CONF_DRIVER)

    from .aesop import aesop

    try:
        cookie = hass.config.path(COOKIE)
        cache = hass.config.path(CACHE)
        session = aesop.get_session(
            username, password, cookie_path=cookie, cache_path=cache, driver=driver
        )
    except aesop.AESOPError:
        _LOGGER.exception("Could not connect to Aesop")
        return False

    hass.data[DATA_AESOP] = AESOPData(session, name)

    for component in AESOP_TYPE:
        discovery.load_platform(hass, component, DOMAIN, {}, config)

    return True


class AESOPData:
    """Stores the data retrieved from AESOP.
    For each entity to use, acts as the single point responsible for fetching updates from the server.
    """

    def __init__(self, session, name):
        """Initialize the data object."""
        self.session = session
        self.name = name
        self.packages = []
        self.mail = []
        self.attribution = None

    @Throttle(MIN_TIME_BETWEEN_UPDATES)
    def update(self, **kwargs):
        """Fetch the latest info from Aesop."""
        from .aesop import aesop

        self.availJobs = aesop.get_availjobs(self.session)
        self.curJobs = aesop.get_curjobs(self.session)
        self.attribution = aesop.ATTRIBUTION
        _LOGGER.debug("Aesop updated at: %s", now().date())
