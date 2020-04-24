import os
import sys

from PyInquirer import prompt, Separator
from termcolor import cprint as print

from .iaction import IAction
from ..tools.configuration import ConfigurationTool, GlobalConfigurationKey, ProjectConfigurationKey
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
		globalConfig = ConfigurationTool.readConfig()

		# Get the project config
		try:
			projectConfig = ConfigurationTool.readConfig(project=True)
		except Exception:
			projectConfig = {}

		# Fill temporary config
		self.config = {}
		self.config[ProjectConfigurationKey.STACK_NAME] = projectConfig[ProjectConfigurationKey.STACK_NAME] if ProjectConfigurationKey.STACK_NAME in projectConfig else os.path.split(os.getcwd())[1]
		self.config[ProjectConfigurationKey.DEV_SUFFIX] = projectConfig[ProjectConfigurationKey.DEV_SUFFIX] if ProjectConfigurationKey.DEV_SUFFIX in projectConfig else True
		self.config[ProjectConfigurationKey.DEV_PROFILE] = projectConfig[ProjectConfigurationKey.DEV_PROFILE] if ProjectConfigurationKey.DEV_PROFILE in projectConfig else "*" + globalConfig[GlobalConfigurationKey.DEV_PROFILE]
		self.config[ProjectConfigurationKey.PROD_PROFILE] = projectConfig[ProjectConfigurationKey.PROD_PROFILE] if ProjectConfigurationKey.PROD_PROFILE in projectConfig else "*" + globalConfig[GlobalConfigurationKey.PROD_PROFILE]
		self.config[ProjectConfigurationKey.DEV_BUCKET] = projectConfig[ProjectConfigurationKey.DEV_BUCKET] if ProjectConfigurationKey.DEV_BUCKET in projectConfig else "*" + globalConfig[GlobalConfigurationKey.DEV_BUCKET]
		self.config[ProjectConfigurationKey.PROD_BUCKET] = projectConfig[ProjectConfigurationKey.PROD_BUCKET] if ProjectConfigurationKey.PROD_BUCKET in projectConfig else "*" + globalConfig[GlobalConfigurationKey.PROD_BUCKET]
		self.config[ProjectConfigurationKey.DEV_REGION] = projectConfig[ProjectConfigurationKey.DEV_REGION] if ProjectConfigurationKey.DEV_REGION in projectConfig else "*" + globalConfig[GlobalConfigurationKey.DEV_REGION] if GlobalConfigurationKey.DEV_REGION in globalConfig else ""
		self.config[ProjectConfigurationKey.PROD_REGION] = projectConfig[ProjectConfigurationKey.PROD_REGION] if ProjectConfigurationKey.PROD_REGION in projectConfig else "*" + globalConfig[GlobalConfigurationKey.PROD_REGION] if GlobalConfigurationKey.PROD_REGION in globalConfig else ""
		

		# Keep showing main config
		while True:
			answer = self._showMainConfig()

			if answer == 1:
				# Ask for name
				self.config[ProjectConfigurationKey.STACK_NAME] = self._askName(default=self.config[ProjectConfigurationKey.STACK_NAME])

			elif answer == 2:
				# Ask if we need to use a suffix
				print("Do you want to use a suffix for the development stack?\nThis can help you distinguish the difference between the stacks if you use the same account for development and production", "yellow")
				self.config[ProjectConfigurationKey.DEV_SUFFIX] = self._askSuffix(default=self.config[ProjectConfigurationKey.DEV_SUFFIX])

			elif answer == 4:				
				# Ask if we want to override the deployment credentials
				devProfileOverride = self._askOverride(default=True if self.config[ProjectConfigurationKey.DEV_PROFILE][0] != "*" else False)
				if devProfileOverride is True:
					# Ask which profile you want to use for deployment
					self.config[ProjectConfigurationKey.DEV_PROFILE] = self._askAWSProfile(default=self.config[ProjectConfigurationKey.DEV_PROFILE])
				else:
					self.config[ProjectConfigurationKey.DEV_PROFILE] = "*" + globalConfig[GlobalConfigurationKey.DEV_PROFILE]

			elif answer == 5:
				# Ask if we want to override the development bucket
				devBucketOverride = self._askOverride(default=True if self.config[ProjectConfigurationKey.DEV_BUCKET][0] != "*" else False)
				if devBucketOverride is True:
					# Ask the name of the Deployment bucket
					self.config[ProjectConfigurationKey.DEV_BUCKET] = self._askS3Bucket(
						profile=self.config[ProjectConfigurationKey.DEV_PROFILE], 
						default=self.config[ProjectConfigurationKey.DEV_BUCKET]
					)
				else:
					self.config[ProjectConfigurationKey.DEV_BUCKET] = "*" + globalConfig[GlobalConfigurationKey.DEV_BUCKET]

			elif answer == 6:
				# Ask if you want to override the region
				self.config[ProjectConfigurationKey.DEV_REGION] = self._askAWSRegion(
					profile=self.config[ProjectConfigurationKey.DEV_PROFILE],
					default=self.config[ProjectConfigurationKey.DEV_REGION]
				)

			elif answer == 8:
				# Ask if we want to override the production credentials
				prodProfileOverride = self._askOverride(default=True if self.config[ProjectConfigurationKey.PROD_PROFILE][0] != "*" else False)
				if prodProfileOverride is True:
					# Ask which profile you want to use for production
					self.config[ProjectConfigurationKey.PROD_PROFILE] = self._askAWSProfile(default=self.config[ProjectConfigurationKey.PROD_PROFILE])
				else:
					self.config[ProjectConfigurationKey.PROD_PROFILE] = "*" + globalConfig[GlobalConfigurationKey.PROD_PROFILE]

			elif answer == 9:
				# Ask if we want to override the product bucket
				prodBucketOverride = self._askOverride(default=True if self.config[ProjectConfigurationKey.PROD_BUCKET][0] != "*" else False)
				if prodBucketOverride is True:
					# Ask the name of the Deployment bucket
					self.config[ProjectConfigurationKey.PROD_BUCKET] = self._askS3Bucket(
						profile=self.config[ProjectConfigurationKey.PROD_PROFILE], 
						default=self.config[ProjectConfigurationKey.PROD_BUCKET]
					)
				else:
					self.config[ProjectConfigurationKey.PROD_BUCKET] = "*" + globalConfig[GlobalConfigurationKey.PROD_BUCKET]

			elif answer == 10:
				# Ask if you want to override the region
				self.config[ProjectConfigurationKey.PROD_REGION] = self._askAWSRegion(
					profile=self.config[ProjectConfigurationKey.PROD_PROFILE],
					default=self.config[ProjectConfigurationKey.PROD_REGION]
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
		choices.append("  Name: %s" % self.config[ProjectConfigurationKey.STACK_NAME])
		choices.append("  Use DEV suffix: %s" % self.config[ProjectConfigurationKey.DEV_SUFFIX])
		choices.append(Separator("~ Development ~"))
		choices.append("  AWS profile: %s" % self.config[ProjectConfigurationKey.DEV_PROFILE])
		choices.append("  AWS bucket: %s" % self.config[ProjectConfigurationKey.DEV_BUCKET])
		choices.append("  AWS region: %s" % self.config[ProjectConfigurationKey.DEV_REGION])
		choices.append(Separator("~ Production ~"))
		choices.append("  AWS profile: %s" % self.config[ProjectConfigurationKey.PROD_PROFILE])
		choices.append("  AWS bucket: %s" % self.config[ProjectConfigurationKey.PROD_BUCKET])
		choices.append("  AWS region: %s" % self.config[ProjectConfigurationKey.PROD_REGION])
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
		config[ProjectConfigurationKey.STACK_NAME] = self.config[ProjectConfigurationKey.STACK_NAME]
		config[ProjectConfigurationKey.DEV_SUFFIX] = self.config[ProjectConfigurationKey.DEV_SUFFIX]
		
		# Check to see if we overridden anything
		if self.config[ProjectConfigurationKey.PROD_PROFILE][0] != "*":
			config[ProjectConfigurationKey.DEV_PROFILE] = devProfile
		if self.config[ProjectConfigurationKey.PROD_PROFILE][0] != "*":
			config[ProjectConfigurationKey.PROD_PROFILE] = prodProfile
		if self.config[ProjectConfigurationKey.PROD_PROFILE][0] != "*":
			config[ProjectConfigurationKey.DEV_BUCKET] = devBucket
		if self.config[ProjectConfigurationKey.PROD_PROFILE][0] != "*":
			config[ProjectConfigurationKey.PROD_BUCKET] = prodBucket
		if self.config[ProjectConfigurationKey.DEV_REGION] not in [None, "", "<empty>"]:
			config[ProjectConfigurationKey.DEV_REGION] = devRegion
		if self.config[ProjectConfigurationKey.DEV_REGION] not in [None, "", "<empty>"]:
			config[ProjectConfigurationKey.PROD_REGION] = prodRegion

		# Check if we have a path
		try:
			ConfigurationTool.getProjectPath()
		except Exception:
			os.makedirs(".pete")

		# Save the config
		ConfigurationTool.saveConfig(config, project=True)

		# Check if there is on template.yaml
		if os.path.exists("template.yaml") is False:
			self._createCloudFormationTemplateFile()

		# Everything is done
		print("All done! You can now use pete deploy in this project. Want to change some details? Just run init again.", "yellow")
		return True

	def _askOverride(self, default=False):
		""" Ask if you want to override
		"""
		# Ask the question
		answer = prompt({
			"type": "confirm",
			"message": "Do you want to override?",
			"name": "override",
			"default": default
		})

		# Check if there is an answer
		if answer == {}:
			sys.exit()

		return answer['override']

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
