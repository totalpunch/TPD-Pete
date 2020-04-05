import os
import sys

from PyInquirer import prompt
from termcolor import cprint as print

from .iaction import IAction
from ..tools.configuration import ConfigurationTool, GlobalConfigurationKey, ProjectConfigurationKey
from ..tools.awscli import AWSCliTool
from ..validator import Validator
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

		# Overview of all the variables
		stackName = projectConfig[ProjectConfigurationKey.STACK_NAME] if ProjectConfigurationKey.STACK_NAME in projectConfig else None
		devProfile = projectConfig[ProjectConfigurationKey.DEV_PROFILE] if ProjectConfigurationKey.DEV_PROFILE in projectConfig else globalConfig[GlobalConfigurationKey.DEV_PROFILE]
		prodProfile = projectConfig[ProjectConfigurationKey.PROD_PROFILE] if ProjectConfigurationKey.PROD_PROFILE in projectConfig else globalConfig[GlobalConfigurationKey.PROD_PROFILE]
		devBucket = projectConfig[ProjectConfigurationKey.DEV_BUCKET] if ProjectConfigurationKey.DEV_BUCKET in projectConfig else globalConfig[GlobalConfigurationKey.DEV_BUCKET]
		prodBucket = projectConfig[ProjectConfigurationKey.PROD_BUCKET] if ProjectConfigurationKey.PROD_BUCKET in projectConfig else globalConfig[GlobalConfigurationKey.PROD_BUCKET]
		devProfileOverride = True if ProjectConfigurationKey.DEV_PROFILE in projectConfig else False
		devBucketOverride = True if ProjectConfigurationKey.DEV_BUCKET in projectConfig else False
		prodProfileOverride = True if ProjectConfigurationKey.PROD_PROFILE in projectConfig else False
		prodBucketOverride = True if ProjectConfigurationKey.PROD_BUCKET in projectConfig else False
		useDevSuffix = projectConfig[ProjectConfigurationKey.DEV_SUFFIX] if ProjectConfigurationKey.DEV_SUFFIX in projectConfig else True

		# Ask the name of the AWS Stack
		print("First: The name of the stack in Cloudformation. What would you like to name this project?", "yellow")
		if stackName is not None:
			currentWorkingFolderName = stackName
		else:
			currentWorkingFolderName = os.path.split(os.getcwd())[1]
		stackName = self._askName(default=currentWorkingFolderName)

		# Ask if we want to override the deployment credentials
		print("Do you want override the global development [%s] profile?" % devProfile, "yellow")
		devProfileOverride = self._askOverride(default=devProfileOverride)
		if devProfileOverride is True:
			# Ask which profile you want to use for deployment
			devProfile = self._askAWSProfile(default=devProfile)

		# Ask if we want to override the production credentials
		print("Do you want to override the global production [%s] profile?" % prodProfile, "yellow")
		prodProfileOverride = self._askOverride(default=prodProfileOverride)
		if prodProfileOverride is True:
			# Ask which profile you want to use for production
			prodProfile = self._askAWSProfile(default=prodProfile)

		# Ask if we want to override the development bucket
		print("Do you want to override the global s3 development [%s] bucket?" % devBucket, "yellow")
		devBucketOverride = self._askOverride(default=devBucketOverride)
		if devBucketOverride is True:
			# Ask the name of the Deployment bucket
			devBucket = self._askS3Bucket(default=devBucket)

		# Ask if we want to override the product bucket
		print("Almost done. Do you want to override the global s3 production [%s] bucket?" % prodBucket, "yellow")
		prodBucketOverride = self._askOverride(default=prodBucketOverride)
		if prodBucketOverride is True:
			# Ask the name of the Deployment bucket
			prodBucket = self._askS3Bucket(default=prodBucket)

		# Ask if we need to use a suffix
		print("Last one. Do you want to use a suffix for the development stack?\nThis can help you distinguish the difference between the stacks if you use the same account for development and production", "yellow")
		useDevSuffix = self._askSuffix(default=useDevSuffix)

		# Create the config
		config = {}
		if devProfileOverride is True:
			config[ProjectConfigurationKey.DEV_PROFILE] = devProfile
		if prodProfileOverride is True:
			config[ProjectConfigurationKey.PROD_PROFILE] = prodProfile
		if devBucketOverride is True:
			config[ProjectConfigurationKey.DEV_BUCKET] = devBucket
		if prodBucketOverride is True:
			config[ProjectConfigurationKey.PROD_PROFILE] = prodBucket
		config[ProjectConfigurationKey.DEV_SUFFIX] = useDevSuffix
		config[ProjectConfigurationKey.STACK_NAME] = stackName

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
