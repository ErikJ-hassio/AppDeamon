import appdaemon.plugins.hass.hassapi as hass
# Global variables

user_ids = {
    "991defd8cdab4044978bff2a052569e7": "erik",
    "2eecb389017b40f4bb5a68c82b8614a2": "ulrika"
}

class Globals(hass.Hass):
    def initialize(self):
        a = 1
