"""Providers"""
import logging
import requests
from . import AuthenticatedBaseException

_LOGGER = logging.getLogger(__name__)

PROVIDERS = {}


def register_provider(classname):
    """Decorator used to register providers."""
    PROVIDERS[classname.name] = classname
    return classname


class GeoProvider:
    """GeoProvider class."""

    url = None

    def __init__(self, ipaddr):
        """Initialize."""
        self.result = {}
        self.ipaddr = ipaddr

    @property
    def country(self):
        """Return country name or None."""
        return self.result.get("country")

    @property
    def region(self):
        """Return region name or None."""
        return self.result.get("region")

    @property
    def city(self):
        """Return city name or None."""
        return self.result.get("city")

    @property
    def computed_result(self):
        """Return the computed result."""
        if self.result is not None:
            return {"country": self.country, "region": self.region, "city": self.city}
        return None

    def update_geo_info(self):
        """Update Geo Information."""
        self.result = {}
        try:
            api = self.url.format(self.ipaddr)
            header = {"user-agent": "Home Assistant/Python"}
            data = requests.get(api, headers=header, timeout=5).json()

            if data.get("error"):
                if data.get("reason") == "RateLimited":
                    raise AuthenticatedBaseException(
                        "RatelimitError, try a different provider."
                    )

            elif data.get("status", "success") == "error":
                return

            elif data.get("reserved"):
                return

            elif data.get("status", "success") == "fail":
                raise AuthenticatedBaseException(
                    "[{}] - {}".format(
                        self.ipaddr, data.get("message", "Unknown error.")
                    )
                )

            self.result = data
            self.parse_data()
        except AuthenticatedBaseException as exception:
            _LOGGER.error(exception)
        except requests.exceptions.ConnectionError:
            pass

    def parse_data(self):
        """Parse data from geoprovider."""
        self.result = self.result


@register_provider
class IPApi(GeoProvider):
    """IPApi class."""

    url = "https://ipapi.co/{}/json"
    name = "ipapi"

    @property
    def country(self):
        """Return country name or None."""
        return self.result.get("country_name")


@register_provider
class ExtremeIPLookup(GeoProvider):
    """IPApi class."""

    url = "https://extreme-ip-lookup.com/json/{}"
    name = "extreme"


@register_provider
class IPVigilante(GeoProvider):
    """IPVigilante class."""

    url = "https://ipvigilante.com/json/{}"
    name = "ipvigilante"

    def parse_data(self):
        """Parse data from geoprovider."""
        self.result = self.result.get("data", {})

    @property
    def country(self):
        """Return country name or None."""
        return self.result.get("country_name")

    @property
    def region(self):
        """Return region name or None."""
        return self.result.get("subdivision_1_name")

    @property
    def city(self):
        """Return city name or None."""
        return self.result.get("city_name")
