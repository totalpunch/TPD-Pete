import json
import os
from enum import Enum
from pathlib import Path


class ConfigType(Enum):
	GLOBAL = "global"
	PROJECT = "project"
	LOCAL = "local"


class ConfigKey(Enum):
	DEV_PROFILE = "dev-profile"
	PROD_PROFILE = "prod-profile"
	DEV_BUCKET = "dev-bucket"
	PROD_BUCKET = "prod-bucket"
	DEV_REGION = "dev-region"
	PROD_REGION = "prod-region"
	DEV_SUFFIX = "dev-suffix"
	STACK_NAME = "stack-name"
	PARAMETERS = "parameters"


class ConfigurationTool(object):
	# Place to hold the config
	config = {}

	@classmethod
	def readConfig(cls, getGlobal=True, getProject=True, getLocal=True):
		""" Read the config
		"""
		# Get the configs
		configs = cls._getConfigPaths(getGlobal=getGlobal, getProject=getProject, getLocal=getLocal)

		# Walk through the paths
		for config in configs:
			# Get the information
			path = config['path']
			configType = config['type']

			# Read the config
			try:
				f = open(path, "r")
				data = json.loads(f.read())
				f.close()
			except Exception:
				raise Exception("Could not read config at '%s'. Delete the file or fix it!" % path)

		# Transform the data
		try:
			cls.config = {}
			for key in data.keys():
				keyName = ConfigKey(key)
				if keyName not in cls.config:
					cls.config[keyName] = {}
				cls.config[keyName][configType] = data[key]
		except Exception:
			raise Exception("Could not read config at '%s'. Delete the file or fix it!" % path)

	@classmethod
	def saveConfig(cls, getGlobal=True, getProject=True, getLocal=True):
		""" Write the config to a file
		"""
		# Get the configs
		configs = cls._getConfigPaths(getGlobal=getGlobal, getProject=getProject, getLocal=getLocal)

		# Walk through the paths
		for config in configs:
			# Get the information
			path = config['path']
			configType = config['type']

			# Check if path exists
			if os.path.exists(os.path.dirname(path)) is False:
				# Create the directories
				os.makedirs(os.path.dirname(path))

			# Replace the ConfigurationKeys
			configData = {}
			for key in cls.config.keys():
				if configType in cls.config[key]:
					if cls.config[key][configType] is not None:
						keyName = key.value
						configData[keyName] = cls.config[key][configType]

			# Write the config
			f = open(path, "w")
			f.write(json.dumps(configData))
			f.close()

	@classmethod
	def getAllConfig(cls, getGlobal=True, getProject=True, getLocal=True):
		""" Get all config
		"""
		# Create a temporary config storage
		config = {}

		# Walk throught the config
		for key in cls.config:
			# Check if local has been filled in
			if ConfigType.LOCAL in cls.config[key] and getLocal is True:
				config[key] = cls.config[key][ConfigType.LOCAL]

			# Check if project has been filled in
			if ConfigType.PROJECT in cls.config[key] and getProject is True:
				config[key] = cls.config[key][ConfigType.PROJECT]

			# Check if global has been filled in
			if ConfigType.GLOBAL in cls.config[key] and getGlobal is True:
				config[key] = cls.config[key][ConfigType.GLOBAL]

		return config

	@classmethod
	def getConfigWithType(cls, key, getGlobal=True, getProject=True, getLocal=True):
		""" Get a specific config value with type

			Returns a specific value
		"""
		# Check if type exists
		if key in cls.config:
			# Check if local has been filled in
			if ConfigType.LOCAL in cls.config[key] and getLocal is True:
				return {"value": cls.config[key][ConfigType.LOCAL], "type": ConfigType.LOCAL}

			# Check if project has been filled in
			if ConfigType.PROJECT in cls.config[key] and getProject is True:
				return {"value": cls.config[key][ConfigType.PROJECT], "type": ConfigType.PROJECT}

			# Check if global has been filled in
			if ConfigType.GLOBAL in cls.config[key] and getGlobal is True:
				return {"value": cls.config[key][ConfigType.GLOBAL], "type": ConfigType.GLOBAL}

		return None

	@classmethod
	def getConfig(cls, key, getGlobal=True, getProject=True, getLocal=True):
		""" Get a specific config value

			Returns a specific value
		"""
		# Check if type exists
		if key in cls.config:
			# Check if local has been filled in
			if ConfigType.LOCAL in cls.config[key] and getLocal is True:
				return cls.config[key][ConfigType.LOCAL]

			# Check if project has been filled in
			if ConfigType.PROJECT in cls.config[key] and getProject is True:
				return cls.config[key][ConfigType.PROJECT]

			# Check if global has been filled in
			if ConfigType.GLOBAL in cls.config[key] and getGlobal is True:
				return cls.config[key][ConfigType.GLOBAL]

		return None

	@classmethod
	def getConfigRow(cls, key):
		""" Get a specific config value row

			Returns a specific value
		"""
		# Check if type exists
		if key in cls.config:
				return cls.config[key]

		return None

	@classmethod
	def _getGlobalPath(cls):
		""" Get the path to the configuration file
		"""
		# Get path to user home dir
		home = str(Path.home())

		# Create the path
		return os.path.join(home, ".pete", "configuration")

	@classmethod
	def _getProjectPath(cls):
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
	def _getConfigPaths(cls, getGlobal=True, getProject=True, getLocal=True):
		""" Get the paths for the config files

			Returns a list
		"""
		# Remember the configs we are going to read
		configs = []

		# Check if we need global config
		if getGlobal is True:
			# Get the file path
			configs.append({"type": ConfigType.GLOBAL, "path": cls._getGlobalPath()})

		# Check if we need global config
		if getGlobal is True:
			# Get the file path
			configs.append({"type": ConfigType.PROJECT, "path": cls._getProjectPath()})

		# Check if we need global config
		if getGlobal is True:
			# Get the file path
			configs.append({"type": ConfigType.LOCAL, "path": cls._getLocalPath()})

		return configs
