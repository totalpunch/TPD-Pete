import json
import os
import subprocess
import sys
import time
import tempfile
from enum import Enum

from halo import Halo
from PyInquirer import prompt
from termcolor import cprint as print

from .iaction import IAction
from ..tools.configuration import ConfigurationTool, ConfigKey, ConfigType
from ..tools.template import TemplateTool


class EnvironmentEnum(Enum):
	DEVELOPMENT = "development"
	PRODUCTION = "production"

	def __str__(self):
		return self.value


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
		ConfigurationTool.readConfig()

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
			try:
				parameters = self._createTemporaryTemplate()
			except Exception as e:
				spinner.fail()
				print(e, "red")
				sys.exit()
			else:
				spinner.succeed()

		# Check if there are other parameters
		parameters = self._checkParameters(parameters)

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
			status = self._cloudformationDeploy(parameters, s3Location)
			if status is True:
				spinner.succeed()
			else:
				spinner.fail()

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
			if ConfigurationTool.getConfig(ConfigKey.DEV_SUFFIX) is True:
				# Add the dev suffix to the items
				template = TemplateTool.addSuffixToItems(template)

		# Add the tags
		template = TemplateTool.addTagsToItems(template)

		# Check the parameters
		template, parameters = TemplateTool.checkVariables(template)

		# Save the template
		f = open(os.path.join(self.location, ".deployment.template.json"), "w")
		f.write(json.dumps(template))
		f.close()

		# Add the basic parameters
		parameters['environment'] = self.environment
		parameters['stackName'] = ConfigurationTool.getConfig(ConfigKey.STACK_NAME) + ("_development" if ConfigurationTool.getConfig(ConfigKey.DEV_SUFFIX) is True and self.environment == EnvironmentEnum.DEVELOPMENT else "")
		parameters['projectName'] = ConfigurationTool.getConfig(ConfigKey.STACK_NAME)

		return parameters

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
			os.environ["VIRTUAL_ENV"] = os.popen("poetry env info -p").read()

		# Check Python virtualenv
		if os.getenv("VIRTUAL_ENV") is not None:
			packagesPath = os.path.join(os.getenv("VIRTUAL_ENV"), "lib", "python%i.%i" % (sys.version_info[0], sys.version_info[1]), "site-packages")
			subprocess.check_call("cp -R %s/. %s/" % (packagesPath, self.location), shell=True)

	def _zipContent(self):
		""" Zip the current directory

			Returns the zip filename
		"""
		# Create a filename
		fileName = "pete_%s.zip" % int(time.time())

		# Build the command
		command = "cd %s && " % self.location
		command = command + "zip -r %s %s " % (fileName, ".")
		command = command + """-x ".git" """
		command = command + """-x ".svn" """
		command = command + """-x ".pete" """
		command = command + """-x ".vscode" """
		command = command + """-x "*.zip" """
		command = command + """-x "seeders/" """
		command = command + """-x ".*" """

		subprocess.check_call(command, shell=True)

		return fileName

	def _uploadToS3(self, zipName):
		""" Upload the zip file to S3
		"""
		# Create a full filename
		fullFileName = "%s/%s" % ((ConfigurationTool.getConfig(ConfigKey.STACK_NAME).lower()), zipName)

		# Get the bucket name and profile
		bucketName = self._getDeploymentBucketName()
		profileName = self._getDeploymentProfile()
		region = self._getDeploymentRegion()

		# Build the full bucket string
		bucketFullFileName = "s3://%s/%s" % (bucketName, fullFileName)

		# Opbouwen van het commando
		command = "cd %s && " % self.location
		command = command + "aws s3 cp %s %s " % (zipName, bucketFullFileName)
		command = command + "--profile %s " % (profileName)
		if region is not None:
			command = command + "--region %s " % (region)

		# Upload the file
		subprocess.check_call(command, shell=True)

		return fullFileName

	def _getDeploymentBucketName(self):
		""" Get the deployment Bucket name from the config

			Returns name of the bucket
		"""
		# Check if we use the development environment
		if self.environment == EnvironmentEnum.DEVELOPMENT:
			# Check if the DEV_BUCKET is in the projectConfig
			bucketName = ConfigurationTool.getConfig(ConfigKey.DEV_BUCKET)

		# This is the production environment
		else:
			# Check if the PROD_BUCKET is in the projectConfig
			bucketName = ConfigurationTool.getConfig(ConfigKey.PROD_BUCKET)

		return bucketName.strip()

	def _getDeploymentProfile(self):
		""" Get the deployment AWS Profile

			Returns name of profile
		"""
		# Check if we use the development environment
		if self.environment == EnvironmentEnum.DEVELOPMENT:
			# Check if the DEV_PROFILE is in the projectConfig
			profileName = ConfigurationTool.getConfig(ConfigKey.DEV_PROFILE)

		# This is the production environment
		else:
			# Check if the PROD_PROFILE is in the projectConfig
			profileName = ConfigurationTool.getConfig(ConfigKey.PROD_PROFILE)

		return profileName.strip()

	def _getDeploymentRegion(self):
		""" Get the deployment AWS Region

			Returns name of region
		"""
		# Default option for region
		region = None

		# Check if we use the development environment
		if self.environment == EnvironmentEnum.DEVELOPMENT:
			# Check if the DEV_REGION is in the projectConfig
			region = ConfigurationTool.getConfig(ConfigKey.DEV_REGION)

		# This is the production environment
		else:
			# Check if the PROD_REGION is in the projectConfig
			region = ConfigurationTool.getConfig(ConfigKey.PROD_REGION)

		return region

	def _cloudformationDeploy(self, parameters, s3Location):
		""" Deploy to CloudFormation
		"""
		# Get the information
		deploymentBucket = self._getDeploymentBucketName()
		profileName = self._getDeploymentProfile()
		region = self._getDeploymentRegion()
		stackName = ConfigurationTool.getConfig(ConfigKey.STACK_NAME)

		# Create the command
		command = "cd %s && " % self.location
		command = command + "aws cloudformation deploy "
		command = command + "--s3-bucket %s " % (deploymentBucket)
		command = command + "--template-file .deployment.template.json "
		command = command + "--stack-name %s " % (stackName)
		command = command + "--profile %s " % (profileName)
		if region is not None:
			command = command + "--region %s " % (region)
		command = command + "--capabilities CAPABILITY_IAM "
		command = command + "--parameter-overrides "
		command = command + "deploymentBucket=\"%s\" " % (deploymentBucket)
		command = command + "s3FileName=\"%s\" " % (s3Location)

		# Walk trought the parameters
		for key, value in parameters.items():
			command = command + """%s="%s" """ % (key, value)

		print(command)

		# Run the command
		try:
			subprocess.check_call(command, shell=True)
		except Exception:
			return False
		return True

	def _checkParameters(self, parameters):
		""" Check if there are other parameters we need information about
		"""
		# Walk through the parameters
		for parameterName in parameters:
			# Check if there is an value
			if parameters[parameterName] in ["String", "Number", "List", "CommaDelimitedList"]:
				# Check if we have the parameter in de project config
				parametersConfig = ConfigurationTool.getConfig(ConfigKey.PARAMETERS)
				if parametersConfig is None:
					parametersConfig = {}

				# Check if the environment exists in the config
				if str(self.environment) in parametersConfig:
					if parameterName in parametersConfig[str(self.environment)]:
						parameters[parameterName] = parametersConfig[str(self.environment)][parameterName]
						continue

				# Ask for the value
				parameterValue, save = self._askForParameterValue(parameterName)

				# Save the value
				parameters[parameterName] = parameterValue

				# Check if we should save the value
				if save is True:
					# Check if the environment exists
					if str(self.environment) not in parametersConfig:
						parametersConfig[str(self.environment)] = {}

					# Set the value in de config
					parametersConfig[str(self.environment)][parameterName] = parameterValue

					# Save the value
					ConfigurationTool.setConfig(ConfigKey.PARAMETERS, parametersConfig, ConfigType.PROJECT)
					ConfigurationTool.saveConfig(ConfigType.PROJECT)

		return parameters

	def _askForParameterValue(self, parameterName):
		""" Ask for the value of an parameter

			Parameters:
				parameterName: Name of the parameter

			Returns tuple (parameterValue, save)
		"""
		# Ask the questions
		answer = prompt([{
			"type": "input",
			"name": "value",
			"message": "What is the value of parameter %s?" % parameterName
		}, {
			"type": "confirm",
			"message": "Do you want to save this value?",
			"name": "save"
		}])

		# Check if there is an answer
		if answer == {}:
			sys.exit()

		return (answer['value'], answer['save'])
