# coding=utf-8
from __future__ import absolute_import

import octoprint.plugin
from octoprint.events import Events
import flask
import board
import os
import digitalio
import time
import threading


class Emergencystopft232hPlugin(octoprint.plugin.AssetPlugin,
                                octoprint.plugin.StartupPlugin,
                                octoprint.plugin.TemplatePlugin,
                                octoprint.plugin.SettingsPlugin,
                                octoprint.plugin.EventHandlerPlugin,
                                octoprint.plugin.ShutdownPlugin,
                                octoprint.plugin.RestartNeedingPlugin,
                                ):

    def __init__(self):
        self.button = None
        self.active = True
        self.estop_sent = False
        self.button_value = True

    def get_settings_defaults(self):
        return dict(
            button_pin="D4"
        )

    def get_template_configs(self):
        return [
            # dict(type="navbar", custom_bindings=True),
            dict(type="settings", custom_bindings=True)
        ]

    def get_assets(self):
        return {
            "js": ["js/EmergencyStopFT232H.js"],
            "css": ["css/EmergencyStopFT232H.css"],
            # "less": ["less/EmergencyStopFT232H.less"]
        }

    def on_after_startup(self):
        self._logger.info("-------------------------------------------------------")
        self._logger.info("Loading emergency stop, and Getting button pin")
        self._logger.info("-------------------------------------------------------")
        self._logger.info("button pin: {}".format(self._settings.get(["button_pin"])))
        self._logger.info("-------------------------------------------------------")
        self.button = digitalio.DigitalInOut(getattr(board, self._settings.get(["button_pin"])))
        self.button.direction = digitalio.Direction.INPUT
        t = threading.Timer(0, self._setup_button)
        t.daemon = True
        t.start()
        self._setup_button()

    def _setup_button(self):
        self.button = digitalio.DigitalInOut(getattr(board, self._settings.get(["button_pin"])))
        self.button.direction = digitalio.Direction.INPUT
        while True:
            if self.button.value is True:
                self._logger.info("Sending emergency stop GCODE")
                self._printer.commands("M112")
                time.sleep(0.2)
                self.active = True
            else:
                if self.button.value is False:
                    self.active = True

    def on_event(self, event, payload):
        if event is Events.CONNECTED:
            self.estop_sent = True
        elif event is Events.DISCONNECTED:
            self.estop_sent = False

    def on_shutdown(self,):
        t.cancel()
        self.active = False

    def get_update_information(self):
        return {
            "EmergencyStopFT232H": {
                "displayName": "Emergencystopft232h Plugin",
                "displayVersion": self._plugin_version,

                "type": "github_release",
                "user": "oldmanbluntz",
                "repo": "OctoPrint-Emergencystopft232h",
                "current": self._plugin_version,

                "pip": "https://github.com/oldmanbluntz/OctoPrint-Emergencystopft232h/archive/{target_version}.zip",
            }
        }


__plugin_name__ = "Emergencystopft232h Plugin"

__plugin_pythoncompat__ = ">=3,<4"  # Only Python 3


def __plugin_load__():
    global __plugin_implementation__
    __plugin_implementation__ = Emergencystopft232hPlugin()

    global __plugin_hooks__
    __plugin_hooks__ = {
        "octoprint.plugin.softwareupdate.check_config": __plugin_implementation__.get_update_information
    }
