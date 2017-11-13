# coding=utf-8
from __future__ import absolute_import

### (Don't forget to remove me)
# This is a basic skeleton for your plugin's __init__.py. You probably want to adjust the class name of your plugin
# as well as the plugin mixins it's subclassing from. This is really just a basic skeleton to get you started,
# defining your plugin as a template plugin, settings and asset plugin. Feel free to add or remove mixins
# as necessary.
#
# Take a look at the documentation on what other plugin mixins are available.
import time
import octoprint.plugin
import flask
from . import neopixels

class NeopixelPlugin(octoprint.plugin.StartupPlugin,
						 octoprint.plugin.SettingsPlugin,
                         octoprint.plugin.AssetPlugin,
                         octoprint.plugin.TemplatePlugin,
						 octoprint.plugin.SimpleApiPlugin):
	
	def on_after_startup(self):
		self._neopixels = neopixels.Neopixels(logger = self._logger,num = self._settings.get(["num"]), pin = self._settings.get(["pin"]), brightness = self._settings.get(["brightness"]))
		self._logger.info("Initialized Neopixels - " + self._identifier)
		self._logger.setLevel("DEBUG")
	##~~ SettingsPlugin mixin

	def get_settings_defaults(self):
		return dict(
			num=10,
			pin=18,
			brightness=255,
			# put your plugin's default settings here
		)

	##~~ AssetPlugin mixin

	def get_assets(self):
		# Define your plugin's asset files to automatically include in the
		# core UI here.
		return dict(
			js=["js/neopixel-pwm.js"],
			css=["css/neopixel-pwm.css"],
			less=["less/neopixel-pwm.less"]
		)

	##~~ Softwareupdate hook

	def get_update_information(self):
		# Define the configuration for your plugin to use with the Software Update
		# Plugin here. See https://github.com/foosel/OctoPrint/wiki/Plugin:-Software-Update
		# for details.
		return dict(
			neopixel=dict(
				displayName="Neopixel Plugin",
				displayVersion=self._plugin_version,

				# version check: github repository
				type="github_release",
				user="birkbjo",
				repo="OctoPrint-Neopixel",
				current=self._plugin_version,

				# update method: pip
				pip="https://github.com/birkbjo/OctoPrint-Neopixel/archive/{target_version}.zip"
			)
		)

	def is_api_adminonly(self):
		return True

	def get_api_commands(self):
		return dict(setState=["r","g","b"], close=['close'], animate=["animation"], clear=[])

	def on_api_command(self, command, data):
		interrupt = True if "interrupt" in data and data["interrupt"] == True else False
		kwargs = data["extra"] if "extra" in data else None
		if command == "setState":
			parameters = ["state", "brightness"]
			#dict with filtered relevant data
			d = { k: data[k] for k in parameters+self.get_api_commands()['setState'] if k in data}
			for k,v in d.iteritems():
				if k == "rgb":
					self._neopixels.rainbow()
			
			#self._logger.info("command1 called, parameter is {parameter}".format(**locals()))
			return flask.jsonify(foo=d)
		elif command == "close":
			self._logger.info("Closing neopixels")
			if data["close"] == True:
				self._neopixels.close()
		elif command == "animate":
			self._neopixels.run_animation(data["animation"], interrupt, kwargs)
			#self._logger.info("command2 called, some_parameter is {some_parameter}".format(**data))
		elif command =="clear":
			self._neopixels.clearQueue(interrupt)
				
	def on_api_get(self, request):
		return flask.jsonify(foo="bar") 

# If you want your plugin to be registered within OctoPrint under a different name than what you defined in setup.py
# ("OctoPrint-PluginSkeleton"), you may define that here. Same goes for the other metadata derived from setup.py that
# can be overwritten via __plugin_xyz__ control properties. See the documentation for that.
__plugin_name__ = "Neopixel Plugin"

def __plugin_load__():
	global __plugin_implementation__
	__plugin_implementation__ = NeopixelPlugin()

	global __plugin_hooks__
	__plugin_hooks__ = {
		"octoprint.plugin.softwareupdate.check_config": __plugin_implementation__.get_update_information
	}

