import os
import sys

from PyInquirer import prompt, Separator
from termcolor import cprint as print

from .iaction import IAction
from ..tools.configuration import ConfigurationTool, ConfigType, ConfigKey
from ..template.template import CLOUDFORMATION_TEMPLATE


class CreateProjectAction(IAction):
	""" The create project action
	"""

	def start(self):
		""" Start the create project action
		"""
		# Just a friendly message
		print("Lets setup this project, I will now ask you some questions. Feel free to answer them.\n", "yellow")

		# Get the global config
		ConfigurationTool.readConfig(getGlobal=True, getProject=True, getLocal=False)

		# Fill temporary config
		self.config = {}
		self.config[ConfigKey.STACK_NAME] = self._getConfigValue(ConfigKey.STACK_NAME)
		self.config[ConfigKey.DEV_SUFFIX] = self._getConfigValue(ConfigKey.DEV_SUFFIX)
		self.config[ConfigKey.DEV_PROFILE] = self._getConfigValue(ConfigKey.DEV_PROFILE)
		self.config[ConfigKey.PROD_PROFILE] = self._getConfigValue(ConfigKey.PROD_PROFILE)
		self.config[ConfigKey.DEV_BUCKET] = self._getConfigValue(ConfigKey.DEV_BUCKET)
		self.config[ConfigKey.PROD_BUCKET] = self._getConfigValue(ConfigKey.PROD_BUCKET)
		self.config[ConfigKey.DEV_REGION] = self._getConfigValue(ConfigKey.DEV_REGION)
		self.config[ConfigKey.PROD_REGION] = self._getConfigValue(ConfigKey.PROD_REGION)

		# Check STACK_NAME
		if self.config[ConfigKey.STACK_NAME] is None:
			self.config[ConfigKey.STACK_NAME] = os.path.split(os.getcwd())[1]

		# Check DEV_SUFFIX
		if self.config[ConfigKey.DEV_SUFFIX] is None:
			self.config[ConfigKey.DEV_SUFFIX] = True

		# Keep showing main config
		while True:
			answer = self._showMainConfig()

			if answer == 1:
				# Ask for name
				self.config[ConfigKey.STACK_NAME] = self._askName(default=self.config[ConfigKey.STACK_NAME])

			elif answer == 2:
				# Ask if we need to use a suffix
				print("Do you want to use a suffix for the development stack?\nThis can help you distinguish the difference between the stacks if you use the same account for development and production", "yellow")
				self.config[ConfigKey.DEV_SUFFIX] = self._askSuffix(default=self.config[ConfigKey.DEV_SUFFIX])

			elif answer == 4:
				# Ask if we want to override the deployment credentials
				devProfileOverride = self._askOverride(default=True if self.config[ConfigKey.DEV_PROFILE][0] != "*" else False)
				if devProfileOverride is True:
					# Ask which profile you want to use for deployment
					self.config[ConfigKey.DEV_PROFILE] = self._askAWSProfile(default=self.config[ConfigKey.DEV_PROFILE])
				else:
					# Return to global value
					self.config[ConfigKey.DEV_PROFILE] = self._getConfigValue(ConfigKey.DEV_PROFILE, getGlobal=True)

			elif answer == 5:
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
					self.config[ConfigKey.DEV_BUCKET] = self._getConfigValue(ConfigKey.DEV_BUCKET, getGlobal=True)

			elif answer == 6:
				# Ask if you want to override the region
				self.config[ConfigKey.DEV_REGION] = self._askAWSRegion(
					profile=self.config[ConfigKey.DEV_PROFILE],
					default=self.config[ConfigKey.DEV_REGION]
				)

			elif answer == 8:
				# Ask if we want to override the production credentials
				prodProfileOverride = self._askOverride(default=True if self.config[ConfigKey.PROD_PROFILE][0] != "*" else False)
				if prodProfileOverride is True:
					# Ask which profile you want to use for production
					self.config[ConfigKey.PROD_PROFILE] = self._askAWSProfile(default=self.config[ConfigKey.PROD_PROFILE])
				else:
					# Return to global value
					self.config[ConfigKey.PROD_PROFILE] = self._getConfigValue(ConfigKey.PROD_PROFILE, getGlobal=True)

			elif answer == 9:
				# Ask if we want to override the product bucket
				prodBucketOverride = self._askOverride(default=True if self.config[ConfigKey.PROD_BUCKET][0] != "*" else False)
				if prodBucketOverride is True:
					# Ask the name of the Deployment bucket
					self.config[ConfigKey.PROD_BUCKET] = self._askS3Bucket(
						profile=self.config[ConfigKey.PROD_PROFILE],
						default=self.config[ConfigKey.PROD_BUCKET]
					)
				else:
					# Return to global value
					self.config[ConfigKey.PROD_BUCKET] = self._getConfigValue(ConfigKey.PROD_BUCKET, getGlobal=True)

			elif answer == 10:
				# Ask if you want to override the region
				self.config[ConfigKey.PROD_REGION] = self._askAWSRegion(
					profile=self.config[ConfigKey.PROD_PROFILE],
					default=self.config[ConfigKey.PROD_REGION]
				)

			elif answer == 11:
				# Save the config
				saved = self._saveConfig()
				if saved is True:
					sys.exit()

	def _showMainConfig(self):
		""" Show the main config options
		"""
		# Make the options for the list
		choices = []
		choices.append(Separator("~ Project ~"))
		choices.append("  Name: %s" % self.config[ConfigKey.STACK_NAME])
		choices.append("  Use DEV suffix: %s" % self.config[ConfigKey.DEV_SUFFIX])
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

	def _getConfigValue(self, key, getGlobal=False):
		""" Get the config value
		"""
		# Get the value from the config
		value = ConfigurationTool.getConfigRow(key)

		# Check if there is an value
		if value is None:
			return None

		# Check if the project value exists
		if ConfigType.PROJECT in value and getGlobal is False:
			return value[ConfigType.PROJECT]

		# Check if global value exists
		elif ConfigType.GLOBAL in value:
			return "*" + value[ConfigType.GLOBAL]

		return None

	def _saveConfig(self):
		""" Save the config
		"""
		# Create the config
		config = {}
		config[ConfigKey.STACK_NAME] = self.config[ConfigKey.STACK_NAME]
		config[ConfigKey.DEV_SUFFIX] = self.config[ConfigKey.DEV_SUFFIX]

		# Check to see if we overridden anything
		if self.config[ConfigKey.DEV_PROFILE][0] != "*":
			config[ConfigKey.DEV_PROFILE] = self.config[ConfigKey.DEV_PROFILE]
		else:
			config[ConfigKey.DEV_PROFILE] = None
		if self.config[ConfigKey.PROD_PROFILE][0] != "*":
			config[ConfigKey.PROD_PROFILE] = self.config[ConfigKey.PROD_PROFILE]
		else:
			config[ConfigKey.PROD_PROFILE] = None
		if self.config[ConfigKey.DEV_BUCKET][0] != "*":
			config[ConfigKey.DEV_BUCKET] = self.config[ConfigKey.DEV_BUCKET]
		else:
			config[ConfigKey.DEV_BUCKET] = None
		if self.config[ConfigKey.PROD_BUCKET][0] != "*":
			config[ConfigKey.PROD_BUCKET] = self.config[ConfigKey.PROD_BUCKET]
		else:
			config[ConfigKey.PROD_BUCKET] = None
		if self.config[ConfigKey.DEV_REGION] not in [None, "", "<empty>"]:
			config[ConfigKey.DEV_REGION] = self.config[ConfigKey.DEV_REGION]
		else:
			config[ConfigKey.DEV_REGION] = None
		if self.config[ConfigKey.DEV_REGION] not in [None, "", "<empty>"]:
			config[ConfigKey.PROD_REGION] = self.config[ConfigKey.PROD_REGION]
		else:
			config[ConfigKey.PROD_REGION] = None

		# Check if we have a path
		try:
			ConfigurationTool._getProjectPath()
		except Exception:
			os.makedirs(".pete")

		# Set the value
		for key in config:
			ConfigurationTool.setConfig(key, config[key], ConfigType.PROJECT)

		# Save the config
		ConfigurationTool.saveConfig(ConfigType.PROJECT)

		# Check if there is on template.yaml
		if os.path.exists("template.yaml") is False:
			# Ask if we should create a CloudFormation template
			if self._askConfirm("Do you want to create a CloudFormation template?") is True:
				# Create an empty CloudFormation template
				self._createCloudFormationTemplateFile()

		# Everything is done
		print("All done! You can now use pete deploy in this project. Want to change some details? Just run init again.", "yellow")
		return True

	def _askSuffix(self, default=True):
		""" Ask if you want to the _DEV suffix
		"""
		# Ask the question
		answer = prompt({
			"type": "confirm",
			"message": "Do you want to use the development suffix?",
			"name": "suffix",
			"default": default
		})

		# Check if there is an answer
		if answer == {}:
			sys.exit()

		return answer['suffix']

	def _createCloudFormationTemplateFile(self):
		""" Create a template.yaml CloudFormation file
		"""
		# Write the content of CLOUDFORMATION_TEMPLATE to the file
		f = open("template.yaml", "w")
		f.write(CLOUDFORMATION_TEMPLATE)
		f.close()
