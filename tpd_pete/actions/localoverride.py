import os
import sys

from PyInquirer import prompt, Separator
from termcolor import cprint as print

from .iaction import IAction
from ..tools.configuration import ConfigurationTool, ConfigType, ConfigKey
from ..validator import Validator


class SetupLocalOverrideAction(IAction):
	""" The setup action
	"""

	def start(self):
		""" Start the setup action
		"""
		# Check if the project has been setup
		if Validator.hasPeteProjectSetup() is False:
			print("You will need to setup the project first, by executing pete init", "orange")
			return

		# Just a friendly message
		print("Lets setup the overrides for the project, I will now ask you some questions. Feel free to answer them.\n", "yellow")

		# Get the global config
		ConfigurationTool.readConfig(getGlobal=True, getProject=True, getLocal=True)

		# Fill temporary config
		self.config = {}
		self.config[ConfigKey.DEV_PROFILE] = self._getConfigValue(ConfigKey.DEV_PROFILE)
		self.config[ConfigKey.DEV_BUCKET] = self._getConfigValue(ConfigKey.DEV_BUCKET)
		self.config[ConfigKey.DEV_REGION] = self._getConfigValue(ConfigKey.DEV_REGION)

		# Keep showing main config
		while True:
			answer = self._showMainConfig()

			if answer == 1:
				# Ask if we want to override the deployment credentials
				devProfileOverride = self._askOverride(default=True if self.config[ConfigKey.DEV_PROFILE][0] != "*" else False)
				if devProfileOverride is True:
					# Ask which profile you want to use for deployment
					self.config[ConfigKey.DEV_PROFILE] = self._askAWSProfile(default=self.config[ConfigKey.DEV_PROFILE])
				else:
					# Return to global value
					self.config[ConfigKey.DEV_PROFILE] = self._getConfigValue(ConfigKey.DEV_PROFILE, getGlobal=True, getProject=True)

			elif answer == 2:
				# Ask if we want to override the development bucket
				devBucketOverride = self._askOverride(default=True if self.config[ConfigKey.DEV_BUCKET][0] != "*" else False)
				if devBucketOverride is True:
					# Ask the name of the Deployment bucket
					self.config[ConfigKey.DEV_BUCKET] = self._askS3Bucket(
						profile=self.config[ConfigKey.DEV_PROFILE],
						default=self.config[ConfigKey.DEV_BUCKET]
					)
				else:
					# Return to global value
					self.config[ConfigKey.DEV_BUCKET] = self._getConfigValue(ConfigKey.DEV_BUCKET, getGlobal=True, getProject=True)

			elif answer == 3:
				# Ask if you want to override the region
				self.config[ConfigKey.DEV_REGION] = self._askAWSRegion(
					profile=self.config[ConfigKey.DEV_PROFILE],
					default=self.config[ConfigKey.DEV_REGION]
				)

			elif answer == 4:
				# Save the config
				saved = self._saveConfig()
				if saved is True:
					sys.exit()

	def _showMainConfig(self):
		""" Show the main config options
		"""
		# Make the options for the list
		choices = []
		choices.append(Separator("~ Development ~"))
		choices.append("  AWS profile: %s" % self.config[ConfigKey.DEV_PROFILE])
		choices.append("  AWS bucket: %s" % self.config[ConfigKey.DEV_BUCKET])
		choices.append("  AWS region: %s" % self.config[ConfigKey.DEV_REGION])
		choices.append("Done")

		# Show the list
		answer = prompt({
			"type": "list",
			"name": "option",
			"message": "Choose an option to configure",
			"choices": choices
		})

		# Check if answer is empty
		if answer == {}:
			sys.exit()

		# Get the index of the option
		index = choices.index(answer['option'])

		return index

	def _saveConfig(self):
		""" Save the config
		"""
		# Create the config
		config = {}

		# Check to see if we overridden anything
		if self.config[ConfigKey.DEV_PROFILE][0] != "*":
			config[ConfigKey.DEV_PROFILE] = self.config[ConfigKey.DEV_PROFILE]
		else:
			config[ConfigKey.DEV_PROFILE] = None
		if self.config[ConfigKey.DEV_BUCKET][0] != "*":
			config[ConfigKey.DEV_BUCKET] = self.config[ConfigKey.DEV_BUCKET]
		else:
			config[ConfigKey.DEV_BUCKET] = None
		if self.config[ConfigKey.DEV_REGION] not in [None, "", "<empty>"]:
			config[ConfigKey.DEV_REGION] = self.config[ConfigKey.DEV_REGION]
		else:
			config[ConfigKey.DEV_REGION] = None

		# Set the value
		for key in config:
			ConfigurationTool.setConfig(key, config[key], ConfigType.LOCAL)

		# Save the config
		ConfigurationTool.saveConfig(ConfigType.LOCAL)

		# Check if there is on template.yaml
		if os.path.exists("template.yaml") is False:
			self._createCloudFormationTemplateFile()

		# Everything is done
		print("All done! You can now use pete deploy in this project. Want to change some details? Just run init again.", "yellow")
		return True

	def _getConfigValue(self, key, getGlobal=False, getProject=False):
		""" Get the config value
		"""
		# Get the value from the config
		value = ConfigurationTool.getConfigRow(key)

		# Check if there is an value
		if value is None:
			return None

		# Check if the local value exists
		if ConfigType.LOCAL in value and getProject is False:
			return value[ConfigType.LOCAL]

		# Check if the project value exists
		if ConfigType.PROJECT in value and getGlobal is False:
			return value[ConfigType.PROJECT]

		# Check if global value exists
		elif ConfigType.GLOBAL in value:
			return "*" + value[ConfigType.GLOBAL]

		return None
