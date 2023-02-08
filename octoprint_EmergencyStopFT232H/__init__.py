# coding=utf-8
from __future__ import absolute_import

import octoprint.plugin
from octoprint.events import Events
import flask
import board
import os
import digitalio


class Emergencystopft232hPlugin(octoprint.plugin.AssetPlugin,
                                octoprint.plugin.StartupPlugin,
                                octoprint.plugin.TemplatePlugin,
                                octoprint.plugin.SettingsPlugin,
                                octoprint.plugin.EventHandlerPlugin,
                                octoprint.plugin.RestartNeedingPlugin
                                ):

    def __init__(self):
        self.button = None
        self.estop_sent = False
        self.button_value = False

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
        self._setup_button()

    def _setup_button(self):
        self.button = digitalio.DigitalInOut(getattr(board, self._settings.get(["button_pin"])))
        self.button.direction = digitalio.Direction.INPUT

    def emergency_stop_triggered(self):
        if self.button.value is True:
            self.send_emergency_stop()
        else:
            self.estop_sent = False
            self._setup_button()

    def send_emergency_stop(self):
        self._logger.info("Sending emergency stop GCODE")
        self._printer.commands("M119")
        self.estop_sent = True
        self._logger.info("de-initializing Button pin")
        self.button.deinit()
        self._logger.info("returning to button setup")
        self._setup_button()

    def on_event(self, event, payload):
        if event is Events.CONNECTED:
            self.estop_sent = True
        elif event is Events.DISCONNECTED:
            self.estop_sent = False

    def get_update_information(self):
        return {
            "EmergencyStopFT232H": {
                "displayName": "EmergencyStopFT232H Plugin",
                "displayVersion": self._plugin_version,

                "type": "github_release",
                "user": "oldmanbluntz",
                "repo": "OctoPrint-EmergencyStopFT232h",
                "current": self._plugin_version,

                "pip": "https://github.com/oldmanbluntz/OctoPrint-EmergencyStopFT232H/archive/{target_version}.zip",
            }
        }


__plugin_name__ = "EmergencyStopFT232H Plugin"

__plugin_pythoncompat__ = ">=3,<4"  # Only Python 3


def __plugin_load__():
    global __plugin_implementation__
    __plugin_implementation__ = Emergencystopft232hPlugin()

    global __plugin_hooks__
    __plugin_hooks__ = {
        "octoprint.plugin.softwareupdate.check_config": __plugin_implementation__.get_update_information
    }
