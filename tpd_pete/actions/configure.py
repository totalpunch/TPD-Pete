import sys

from PyInquirer import prompt, Separator
from termcolor import cprint as print

from .iaction import IAction
from ..tools.configuration import ConfigurationTool, GlobalConfigurationKey
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
			data = ConfigurationTool.readConfig()
		else:
			data = {}

		# Fill temporary config
		self.config = {}
		self.config[GlobalConfigurationKey.DEV_PROFILE] = data[GlobalConfigurationKey.DEV_PROFILE] if GlobalConfigurationKey.DEV_PROFILE in data else "<empty>"
		self.config[GlobalConfigurationKey.DEV_BUCKET] = data[GlobalConfigurationKey.DEV_BUCKET] if GlobalConfigurationKey.DEV_BUCKET in data else "<empty>"
		self.config[GlobalConfigurationKey.DEV_REGION] = data[GlobalConfigurationKey.DEV_REGION] if GlobalConfigurationKey.DEV_REGION in data else ""
		self.config[GlobalConfigurationKey.PROD_PROFILE] = data[GlobalConfigurationKey.PROD_PROFILE] if GlobalConfigurationKey.PROD_PROFILE in data else "<empty>"
		self.config[GlobalConfigurationKey.PROD_BUCKET] = data[GlobalConfigurationKey.PROD_BUCKET] if GlobalConfigurationKey.PROD_BUCKET in data else "<empty>"
		self.config[GlobalConfigurationKey.PROD_REGION] = data[GlobalConfigurationKey.PROD_REGION] if GlobalConfigurationKey.PROD_REGION in data else ""

		# Keep showing main config
		while True:
			answer = self._showMainConfig()

			if answer == 1:
				# Ask development profile
				self.config[GlobalConfigurationKey.DEV_PROFILE] = self._askAWSProfile(default=self.config[GlobalConfigurationKey.DEV_PROFILE] if self.config[GlobalConfigurationKey.DEV_PROFILE] != "<empty>" else None)

			elif answer == 2:
				# Ask development bucket
				self.config[GlobalConfigurationKey.DEV_BUCKET] = self._askS3Bucket(
					profile=self.config[GlobalConfigurationKey.DEV_PROFILE],
					default=self.config[GlobalConfigurationKey.DEV_BUCKET] if self.config[GlobalConfigurationKey.DEV_BUCKET] != "<empty>" else None
				)

			elif answer == 3:
				# Ask development region
				self.config[GlobalConfigurationKey.DEV_REGION] = self._askAWSRegion(
					profile=self.config[GlobalConfigurationKey.DEV_PROFILE],
					default=self.config[GlobalConfigurationKey.DEV_REGION] if self.config[GlobalConfigurationKey.DEV_REGION] != "<empty>" else None
				)

			elif answer == 5:
				# Ask production profile
				self.config[GlobalConfigurationKey.PROD_PROFILE] = self._askAWSProfile(default=self.config[GlobalConfigurationKey.PROD_PROFILE] if self.config[GlobalConfigurationKey.PROD_PROFILE] != "<empty>" else None)

			elif answer == 6:
				# Ask production bucket
				self.config[GlobalConfigurationKey.PROD_BUCKET] = self._askS3Bucket(
					profile=self.config[GlobalConfigurationKey.PROD_PROFILE],
					default=self.config[GlobalConfigurationKey.PROD_BUCKET] if self.config[GlobalConfigurationKey.PROD_BUCKET] != "<empty>" else None
				)

			elif answer == 7:
				# Ask production region
				self.config[GlobalConfigurationKey.PROD_REGION] = self._askAWSRegion(
					profile=self.config[GlobalConfigurationKey.PROD_PROFILE],
					default=self.config[GlobalConfigurationKey.PROD_REGION] if self.config[GlobalConfigurationKey.PROD_REGION] != "<empty>" else None
				)

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
		choices.append("  AWS profile: %s" % self.config[GlobalConfigurationKey.DEV_PROFILE])
		choices.append("  AWS bucket: %s" % self.config[GlobalConfigurationKey.DEV_BUCKET])
		choices.append("  AWS region: %s" % self.config[GlobalConfigurationKey.DEV_REGION])
		choices.append(Separator("~ Production ~"))
		choices.append("  AWS profile: %s" % self.config[GlobalConfigurationKey.PROD_PROFILE])
		choices.append("  AWS bucket: %s" % self.config[GlobalConfigurationKey.PROD_BUCKET])
		choices.append("  AWS region: %s" % self.config[GlobalConfigurationKey.PROD_REGION])
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
		""" Save the config to file
		"""
		# Check the data
		for key, value in self.config.items():
			# Cant save empty values
			if value == "<empty>":
				return False

		# Build a new config
		data = {}

		# Combine the data
		data[GlobalConfigurationKey.DEV_PROFILE] = self.config[GlobalConfigurationKey.DEV_PROFILE]
		data[GlobalConfigurationKey.PROD_PROFILE] = self.config[GlobalConfigurationKey.PROD_PROFILE]
		data[GlobalConfigurationKey.DEV_BUCKET] = self.config[GlobalConfigurationKey.DEV_BUCKET]
		data[GlobalConfigurationKey.PROD_BUCKET] = self.config[GlobalConfigurationKey.PROD_BUCKET]
		if self.config[GlobalConfigurationKey.DEV_REGION] not in [None, "", "<empty>"]:
			data[GlobalConfigurationKey.DEV_REGION] = self.config[GlobalConfigurationKey.DEV_REGION]
		if self.config[GlobalConfigurationKey.PROD_REGION] not in [None, "", "<empty>"]:
			data[GlobalConfigurationKey.PROD_REGION] = self.config[GlobalConfigurationKey.PROD_REGION]

		# Save the config
		ConfigurationTool.saveConfig(data)

		# Everything is done
		print("All done! You can now use pete init or deploy in your projects", "yellow")
		return True
