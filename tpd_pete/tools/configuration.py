import json
import os
from enum import Enum
from pathlib import Path


class GlobalConfigurationKey(Enum):
	DEV_PROFILE = "dev-profile"
	PROD_PROFILE = "prod-profile"
	DEV_BUCKET = "dev-bucket"
	PROD_BUCKET = "prod-bucket"


class ProjectConfigurationKey(Enum):
	DEV_PROFILE = "dev-profile"
	PROD_PROFILE = "prod-profile"
	DEV_BUCKET = "dev-bucket"
	PROD_BUCKET = "prod-bucket"
	DEV_SUFFIX = "dev-suffix"
	STACK_NAME = "stack-name"
	PARAMETERS = "parameters"


class ConfigurationTool(object):

	@classmethod
	def getGlobalPath(cls):
		""" Get the path to the configuration file
		"""
		# Get path to user home dir
		home = str(Path.home())

		# Create the path
		return os.path.join(home, ".pete", "configuration")

	@classmethod
	def getProjectPath(cls):
		""" Get the path to the project configuration files
		"""
		# Get the current working dir
		workingDir = os.getcwd()
		path = None

		# Search for the pete folder
		while True:
			# Check if we reached the top
			if os.path.ismount(workingDir) is True:
				break

			# Check if a directory exists
			if ".pete" in os.listdir(workingDir):
				path = workingDir
				break

			# Move a directory up
			workingDir = os.path.dirname()[0]

		# Check if we found a path
		if path is None:
			raise Exception("Could not find the configuration file. Did you run init for this project?")

		return os.path.join(path, ".pete", "configuration")

	@classmethod
	def readConfig(cls, project=False):
		""" Read the config
		"""
		# Check if we need global config
		if project is False:
			# Get the file path
			path = cls.getGlobalPath()
		else:
			path = cls.getProjectPath()


		# Read the config
		try:
			f = open(path, "r")
			data = json.loads(f.read())
			f.close()
		except Exception:
			raise Exception("Could not read config at '%s'. Delete the file or fix it!" % path)

		# Transform the data to GlobalConfigurationKey
		try:
			config = {}
			for key in data.keys():
				if project is False:
					keyName = GlobalConfigurationKey(key)
				else:
					keyName = ProjectConfigurationKey(key)
				config[keyName] = data[key]
		except Exception:
			raise Exception("Could not read config at '%s'. Delete the file or fix it!" % path)

		return config

	@classmethod
	def saveConfig(cls, data, project=False):
		""" Write the config to a file
		"""
		# Check if this is the global config
		if project is False:
			# Get the file path
			path = cls.getGlobalPath()
		else:
			path = cls.getProjectPath()

		# Check if path exists
		if os.path.exists(os.path.dirname(path)) is False:
			# Create the directories
			os.makedirs(os.path.dirname(path))

		# Replace the ConfigurationKeys
		config = {}
		for key in data.keys():
			keyName = key.value
			config[keyName] = data[key]

		# Write the config
		f = open(path, "w")
		f.write(json.dumps(config))
		f.close()
