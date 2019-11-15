from aiohttp import web
from homeassistant.components.http import HomeAssistantView
import os.path

def setup_view(hass, name):
    hass.http.register_view(CustomComponentServer(hass, name))

class CustomComponentServer(HomeAssistantView):

    requires_auth = False

    def __init__(self, hass, domain):
        self.name = domain+"_server"
        self.url = '/'+domain+'/{filename:.*}'
        self.config_dir = hass.config.path()
        self.domain = domain

    async def get(self, request, filename):
        path = os.path.join(self.config_dir, 'custom_components', self.domain, filename)
        filecontent = ""

        try:
            with open(path, mode="r", encoding="utf-8", errors="ignore") as localfile:
                filecontent = localfile.read()
                localfile.close()
        except Exception as exception:
            return web.Response(status=404)

        return web.Response(body=filecontent, content_type="text/javascript", charset="utf-8")
