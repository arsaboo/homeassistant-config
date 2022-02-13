"""Constants for authenticated."""

DOMAIN = "authenticated"
INTEGRATION_VERSION = "21.9.0"
ISSUE_URL = "https://github.com/custom-components/authenticated/issues"

STARTUP = f"""
-------------------------------------------------------------------
{DOMAIN}
Version: {INTEGRATION_VERSION}
This is a custom component
If you have any issues with this you need to open an issue here:
https://github.com/custom-components/authenticated/issues
-------------------------------------------------------------------
"""


CONF_NOTIFY = "enable_notification"
CONF_EXCLUDE = "exclude"
CONF_EXCLUDE_CLIENTS = "exclude_clients"
CONF_PROVIDER = "provider"
CONF_LOG_LOCATION = "log_location"

OUTFILE = ".ip_authenticated.yaml"
