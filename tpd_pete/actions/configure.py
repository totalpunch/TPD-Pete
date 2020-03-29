import sys

from PyInquirer import prompt
from termcolor import cprint as print

from .iaction import IAction
from ..tools.configuration import ConfigurationTool, GlobalConfigurationKey
from ..tools.awscli import AWSCliTool
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

		# Ask which profile you want to use for deployment
		print("First up your Development profile.\nAll of these settings are global. You can override them in your projects, if you need too.", "yellow")
		devProfile = self._askAWSProfile(default=data[GlobalConfigurationKey.DEV_PROFILE] if GlobalConfigurationKey.DEV_PROFILE in data else None)

		# Ask which profile you want to use for production
		print("Next Production profile.", "yellow")
		prodProfile = self._askAWSProfile(default=data[GlobalConfigurationKey.PROD_PROFILE] if GlobalConfigurationKey.PROD_PROFILE in data else None)

		# Ask for the deployment S3 bucket
		print("Now where do you want the Development code to be uploaded?", "yellow")
		devBucket = self._askS3Bucket(default=data[GlobalConfigurationKey.DEV_BUCKET] if GlobalConfigurationKey.DEV_BUCKET in data else None)

		# Ask for the production S3 bucket
		print("Up next: Where do you want the Production code to be uploaded?", "yellow")
		prodBucket = self._askS3Bucket(default=data[GlobalConfigurationKey.PROD_BUCKET] if GlobalConfigurationKey.PROD_BUCKET in data else None)

		# Combine the data
		data[GlobalConfigurationKey.DEV_PROFILE] = devProfile
		data[GlobalConfigurationKey.PROD_PROFILE] = prodProfile
		data[GlobalConfigurationKey.DEV_BUCKET] = devBucket
		data[GlobalConfigurationKey.PROD_BUCKET] = prodBucket

		# Save the config
		ConfigurationTool.saveConfig(data)

		# Everything is done
		print("All done! You can now use pete init or deploy in your projects", "yellow")
