import json
import os
import subprocess
import shutil
import sys
import time
import tempfile
from enum import Enum, auto as autoEnum

from halo import Halo
from termcolor import cprint as print

from .iaction import IAction
from ..tools.configuration import ConfigurationTool, GlobalConfigurationKey, ProjectConfigurationKey
from ..tools.awscli import AWSCliTool
from ..tools.template import TemplateTool
from ..validator import Validator


class EnvironmentEnum(Enum):
	DEVELOPMENT = autoEnum()
	PRODUCTION = autoEnum()


class DeploymentAction(IAction):
	""" The deployment action
	"""

	def __init__(self):
		""" Init the action
		"""
		# Initialize the parent
		super().__init__()

		# Set the default environment to development
		self.environment = EnvironmentEnum.DEVELOPMENT

	def start(self, **kwargs):
		""" Start the deployment
		"""
		# Get the configs
		self.globalConfig = ConfigurationTool.readConfig()
		self.projectConfig = ConfigurationTool.readConfig(project=True)

		# Check if there is an template
		if os.path.exists("template.yaml") is False:
			raise Exception("Cant find CloudFormation template: 'template.yaml'")

		# Check if it is the production environment
		if kwargs['production'] is True:
			self.environment = EnvironmentEnum.PRODUCTION

		# Create a temporary directory
		with Halo(text="Creating environment") as spinner:
			self._createTempDir()
			spinner.succeed()

		# Create a new temporary template
		with Halo(text="Creating template") as spinner:
			parameters = self._createTemporaryTemplate()
			spinner.succeed()

		# Check the dependencies
		with Halo(text="Installing dependencies") as spinner:
			self._checkDependencies()
			spinner.succeed()

		# Zip it all
		with Halo(text="Zipping content") as spinner:
			zipName = self._zipContent()
			spinner.succeed()

		# Upload the zip
		with Halo(text="Uploading to S3") as spinner:
			s3Location = self._uploadToS3(zipName)
			spinner.succeed()

		# Send it to CloudFormation
		with Halo(text="CloudFormation deploying") as spinner:
			self._cloudformationDeploy(parameters, s3Location)
			spinner.succeed()


	def _createTempDir(self):
		""" Create a temporary directory for deployment

			Returns path
		"""
		# Create the directory
		self.location = tempfile.mkdtemp()

		# Copy all the current files to it
		subprocess.check_call("cp -R %s %s" % (".", self.location), shell=True)

		return self.location

	def _createTemporaryTemplate(self):
		""" Create a temporary template

			Returns a dict with the parameters
		"""
		# Get the template
		f = open("template.yaml", "r")
		template = f.read()
		f.close()
		template = TemplateTool.parseTemplate(template)

		# Check the environment
		if self.environment == EnvironmentEnum.DEVELOPMENT:
			if self.projectConfig[ProjectConfigurationKey.DEV_SUFFIX] is True:
				# Add the dev suffix to the items
				template = TemplateTool.addSuffixToItems(template)

		# Add the tags
		template = TemplateTool.addTagsToItems(template)

		# Check the parameters
		template = TemplateTool.checkVariables(template)

		# Save the template
		f = open(os.path.join(self.location, ".deployment.template.json"), "w")
		f.write(json.dumps(template))
		f.close()

		return {
			"environment": self.environment,
			"stackName": self.projectConfig[ProjectConfigurationKey.STACK_NAME] + ("_development" if self.projectConfig[ProjectConfigurationKey.DEV_SUFFIX] is True and self.environment == EnvironmentEnum.DEVELOPMENT else ""),
			"projectName": self.projectConfig[ProjectConfigurationKey.STACK_NAME]
		}

	def _checkDependencies(self):
		""" Check which dependencies we should install
		"""
		# Check NodeJS 'package.json'
		if os.path.exists("package.json") is True:
			subprocess.check_call("npm install --prefix %s" % self.location, shell=True)

		# Check Python 'requirements.txt'
		if os.path.exists("requirements.txt") is True:
			subprocess.check_call("pip install -r requirements.txt -t %s" % self.location, shell=True)

		# Check Python 'poetry.lock'
		if os.path.exists("poetry.lock") is True:
			subprocess.check_call("poetry install", shell=True)

		# Check Python virtualenv
		if os.getenv("VIRTUAL_ENV") is not None:
			packagesPath = os.path.join(os.getenv("VIRTUAL_ENV"), "lib", "python%i.%i" % (sys.version_info[0], sys.version_info[1]), "site-packages")
			subprocess.check_call("cp -R %s %s" % (packagesPath, self.location), shell=True)

	def _zipContent(self):
		""" Zip the current directory

			Returns the zip filename
		"""
		# Create a filename
		fileName = os.path.join(self.location, "pete_%s.zip" % int(time.time()))

		# Zip it
		subprocess.check_call("""zip -r %s %s -x ".git" -x ".svn" -x ".pete" -x ".vscode" -x "*.zip" -x "seeders/" -x ".*" """ % (fileName, self.location), shell=True)

		return fileName

	def _uploadToS3(self, zipName):
		""" Upload the zip file to S3
		"""
		# Create a full filename
		fullFileName="%s/%s" % ((self.projectConfig[ProjectConfigurationKey.STACK_NAME].lower()), zipName)

		# Get the bucket name
		bucketName = self._getDeploymentBucketName()

		# Build the full bucket string
		fullFileName = "s3://%s/%s" % (bucketName, fullFileName)

		# Upload the file
		subprocess.check_call("aws s3 cp %s %s" % (zipName, fullFileName), shell=True)

		return fullFileName

	def _getDeploymentBucketName(self):
		""" Get the deployment Bucket name from the config

			Returns name of the bucket
		"""
		# Check if we use the development environment
		if self.environment == EnvironmentEnum.DEVELOPMENT:
			# Check if the DEV_BUCKET is in the projectConfig
			if ProjectConfigurationKey.DEV_BUCKET in self.projectConfig:
				# Use the project override
				bucketName = self.projectConfig[ProjectConfigurationKey.DEV_BUCKET]
			else:
				# Use the global bucket
				bucketName = self.globalConfig[GlobalConfigurationKey.DEV_BUCKET]

		# This is the production environment
		else:
			# Check if the PROD_BUCKET is in the projectConfig
			if ProjectConfigurationKey.PROD_BUCKET in self.projectConfig:
				# Use the project override
				bucketName = self.projectConfig[ProjectConfigurationKey.PROD_BUCKET]
			else:
				# Use the global bucket
				bucketName = self.globalConfig[GlobalConfigurationKey.PROD_BUCKET]

		return bucketName.strip()

	def _cloudformationDeploy(self, parameters, s3Location):
		""" Deploy to CloudFormation
		"""
		# Get the information
		deploymentBucket = self._getDeploymentBucketName()
		stackName = self.projectConfig[ProjectConfigurationKey.STACK_NAME]

		# Create the command
		command = "aws cloudformation deploy "
		command = command + "--s3-bucket %s" % (deploymentBucket)
		command = command + "--template-file .deployment.template.json"
		command = command + "--stack-name %s " % (stackName)
		command = command + "--capabilities CAPABILITY_IAM "
		command = command + """--parameter-overrides deploymentBucket="%s" """ % (deploymentBucket)
		command = command + """--parameter-overrides s3FileName="%s" """ % (s3Location)

		# Walk trought the parameters
		for key, value in parameters.items():
			command = command + """--parameter-overrides %s="%s" """ % (key, value)

		# Run the command
		subprocess.check_call(command, shell=True)
