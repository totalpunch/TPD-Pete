import sys

from PyInquirer import prompt, Separator
from termcolor import cprint as print

from .iaction import IAction
from ..tools.configuration import ConfigurationTool, ConfigKey, ConfigType
from ..validator import Validator


class ConfigureAction(IAction):
	""" The configure action
	"""

	def start(self):
		""" Start the configure action
		"""
		# Just a friendly message
		print("Lets configure TPD Pete, I will now ask you some questions. Feel free to answer them.\n", "yellow")

		# Check if there is already a config
		if Validator.hasPeteSetup() is True:
			ConfigurationTool.readConfig(getGlobal=True, getProject=False, getLocal=False)

		# Fill temporary config
		self.config = {}
		self.config[ConfigKey.DEV_PROFILE] = self._getConfigValue(ConfigKey.DEV_PROFILE)
		self.config[ConfigKey.PROD_PROFILE] = self._getConfigValue(ConfigKey.PROD_PROFILE)
		self.config[ConfigKey.DEV_BUCKET] = self._getConfigValue(ConfigKey.DEV_BUCKET)
		self.config[ConfigKey.PROD_BUCKET] = self._getConfigValue(ConfigKey.PROD_BUCKET)
		self.config[ConfigKey.DEV_REGION] = self._getConfigValue(ConfigKey.DEV_REGION)
		self.config[ConfigKey.PROD_REGION] = self._getConfigValue(ConfigKey.PROD_REGION)

		# Keep showing main config
		while True:
			answer = self._showMainConfig()

			if answer == 1:
				# Ask development profile
				defaultValue = self._getConfigValue(ConfigKey.DEV_PROFILE)
				value = self._askAWSProfile(default=defaultValue)
				self.setValue(ConfigKey.DEV_PROFILE, value)

			elif answer == 2:
				# Ask development bucket
				profile = self._getConfigValue(ConfigKey.DEV_PROFILE)
				if profile is None:
					print("Configure the profile first", "orange")
					continue
				defaultValue = self._getConfigValue(ConfigKey.DEV_BUCKET)
				value = self._askS3Bucket(profile=profile, default=defaultValue)
				self.setValue(ConfigKey.DEV_BUCKET, value)

			elif answer == 3:
				# Ask development region
				profile = self._getConfigValue(ConfigKey.DEV_PROFILE)
				if profile is None:
					print("Configure the profile first", "orange")
					continue
				defaultValue = self._getConfigValue(ConfigKey.DEV_REGION)
				value = self._askAWSRegion(profile=profile, default=defaultValue)
				self.setValue(ConfigKey.DEV_REGION, value)

			elif answer == 5:
				# Ask production profile
				defaultValue = self._getConfigValue(ConfigKey.PROD_PROFILE)
				value = self._askAWSProfile(default=defaultValue)
				self.setValue(ConfigKey.PROD_PROFILE, value)

			elif answer == 6:
				# Ask production bucket
				profile = self._getConfigValue(ConfigKey.PROD_PROFILE)
				if profile is None:
					print("Configure the profile first", "orange")
					continue
				defaultValue = self._getConfigValue(ConfigKey.PROD_BUCKET)
				value = self._askS3Bucket(profile=profile, default=defaultValue)
				self.setValue(ConfigKey.PROD_BUCKET, value)

			elif answer == 7:
				# Ask production region
				profile = self._getConfigValue(ConfigKey.PROD_PROFILE)
				if profile is None:
					print("Configure the profile first", "orange")
					continue
				defaultValue = self._getConfigValue(ConfigKey.PROD_REGION)
				value = self._askAWSRegion(profile=profile, default=defaultValue)
				self.setValue(ConfigKey.PROD_REGION, value)

			elif answer == 8:
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
		choices.append(Separator("~ Production ~"))
		choices.append("  AWS profile: %s" % self.config[ConfigKey.PROD_PROFILE])
		choices.append("  AWS bucket: %s" % self.config[ConfigKey.PROD_BUCKET])
		choices.append("  AWS region: %s" % self.config[ConfigKey.PROD_REGION])
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

	def _getConfigValue(self, key):
		""" Get the config value
		"""
		# Get the value from the config
		value = ConfigurationTool.getConfigRow(key)

		# Check if there is an value
		if value is None:
			return None

		# Check if global value exists
		if ConfigType.GLOBAL in value:
			return value[ConfigType.GLOBAL]

		return None

	def setValue(self, key, value):
		""" Set a config value
		"""
		self.config[key] = value
		ConfigurationTool.setConfig(key, value, ConfigType.GLOBAL)

	def _saveConfig(self):
		""" Save the config to file
		"""
		# Save the config
		ConfigurationTool.saveConfig(ConfigType.GLOBAL)

		# Everything is done
		print("All done! You can now use pete init or deploy in your projects", "yellow")
		return True
