"""
A platform which allows you to get information about sucessfull logins to Home Assistant.
For more details about this component, please refer to the documentation at
https://github.com/custom-components/sensor.authenticated
"""
from datetime import timedelta
from pathlib import Path
import requests
import yaml
from homeassistant.helpers.entity import Entity

ATTR_COUNTRY = 'country'
ATTR_REGION = 'region'
ATTR_CITY = 'city'

SCAN_INTERVAL = timedelta(seconds=30)

PLATFORM_NAME = 'authenticated'
PLATFORM_VERSION = '0.0.2'

LOGFILE = 'home-assistant.log'
OUTFILE = '.ip_authenticated.yaml'

def setup_platform(hass, config, add_devices, discovery_info=None):
    """Create the sensor"""
    logs = {'homeassistant.components.http.view': 'info'}
    hass.services.call('logger', 'set_level', logs)
    log = str(hass.config.path(LOGFILE))
    out = str(hass.config.path(OUTFILE))
    add_devices([Authenticated(hass, log, out)])

class Authenticated(Entity):
    """Representation of a Sensor."""

    def __init__(self, hass, log, out):
        """Initialize the sensor."""
        self._state = None
        self._country = None
        self._region = None
        self._city = None
        self._log = log
        self._out = out
        self.hass = hass
        self.update()

    def first_ip(self, ip_address, access_time):
        """If the IP is the first"""
        with open(self._out, 'a') as the_file:
            the_file.write(ip_address + ':')
        self.new_ip(ip_address, access_time)

    def new_ip(self, ip_address, access_time):
        """If the IP is new"""
        fetchurl = 'https://ipapi.co/' + ip_address + '/json/'
        try:
            geo = requests.get(fetchurl, timeout=5).json()
        except:
            geo = 'none'
        else:
            geo = geo
        if 'reserved' in geo:
            geo_country = 'none'
            geo_region = 'none'
            geo_city = 'none'
        else:
            geo_country = geo['country']
            geo_region = geo['region']
            geo_city = geo['city']
        self.write_file(ip_address, access_time, geo_country, geo_region, geo_city)
        self.hass.components.persistent_notification.create('{}'.format(ip_address
            + ' (' + geo_country + ', ' + geo_region + ', ' + geo_city + ')'), 'New successful login from')

    def update_ip(self, ip_address, access_time):
        """If we know this IP"""
        with open(self._out) as f:
            doc = yaml.load(f)

        doc[ip_address]['last_authenticated'] = access_time

        with open(self._out, 'w') as f:
            yaml.dump(doc, f, default_flow_style=False)

    def write_file(self, ip_address, access_time, country='none', region='none', city='none'):
        """Writes info to out control file"""
        with open(self._out) as f:
            doc = yaml.load(f)

        doc[ip_address] = dict(
            last_authenticated=access_time,
            country=country,
            region=region,
            city=city
        )

        with open(self._out, 'w') as f:
            yaml.dump(doc, f, default_flow_style=False)


    def update(self):
        """Method to update sensor value"""
        get_ip = None
        with open(self._log) as f:
            for line in reversed(f.readlines()):
                if '(auth: True)' in line:
                    get_ip = line
                    break
        if get_ip is None:
            self._state = None
        else:
            ip_address = get_ip.split(' ')[8]
            access_time = get_ip.split(' ')[0] + ' ' + get_ip.split(' ')[1]

            checkpath = Path(self._out)
            if checkpath.exists():
                if str(ip_address) in open(self._out).read():
                    self.update_ip(ip_address, access_time)
                else:
                    self.new_ip(ip_address, access_time)
            else:
                self.first_ip(ip_address, access_time)
            self._state = ip_address
            stream = open(self._out, 'r')
            geo_info = yaml.load(stream)
            self._country = geo_info[ip_address]['country']
            self._region = geo_info[ip_address]['region']
            self._city = geo_info[ip_address]['city']

    @property
    def name(self):
        """Return the name of the sensor."""
        return 'Last sucessfull authentication'

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def icon(self):
        """Return the icon of the sensor."""
        return 'mdi:security-lock'

    @property
    def device_state_attributes(self):
        """Return attributes for the sensor."""
        return {
            ATTR_COUNTRY: self._country,
            ATTR_REGION: self._region,
            ATTR_CITY: self._city,
        }
