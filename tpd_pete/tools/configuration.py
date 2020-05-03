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
		configTypes = []
		if getGlobal is True:
			configTypes.append(ConfigType.GLOBAL)
		if getProject is True:
			configTypes.append(ConfigType.PROJECT)
		if getLocal is True:
			configTypes.append(ConfigType.LOCAL)
		configs = cls._getConfigPaths(configTypes)

		# Empty the config
		cls.config = {}

		# Walk through the paths
		for config in configs:
			# Get the information
			path = config['path']
			configType = config['type']

			# Check if the location exists
			if path is None or os.path.exists(path) is False:
				continue

			# Read the config
			try:
				f = open(path, "r")
				data = json.loads(f.read())
				f.close()
			except Exception:
				raise Exception("Could not read config at '%s'. Delete the file or fix it!" % path)

			# Transform the data
			try:
				for key in data.keys():
					keyName = ConfigKey(key)
					if keyName not in cls.config:
						cls.config[keyName] = {}
					cls.config[keyName][configType] = data[key]
			except Exception:
				raise Exception("Could not read config at '%s'. Delete the file or fix it!" % path)

	@classmethod
	def saveConfig(cls, configType):
		""" Write the config to a file
		"""
		# Get the configs
		configs = cls._getConfigPaths([configType])

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
	def getAllConfig(cls, getGlobal=True, getProject=True, getLocal=True, emptyValue=None):
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

		# Check if all keys exists
		for key in ConfigKey:
			if key not in config:
				config[key] = emptyValue

		return config

	@classmethod
	def getConfigWithType(cls, key, getGlobal=True, getProject=True, getLocal=True, emptyValue=None):
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

		return emptyValue

	@classmethod
	def getConfig(cls, key, getGlobal=True, getProject=True, getLocal=True, emptyValue=None):
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

		return emptyValue

	@classmethod
	def getConfigRow(cls, key, emptyValue=None):
		""" Get a specific config value row

			Returns a specific value
		"""
		# Check if type exists
		if key in cls.config:
				return cls.config[key]

		return emptyValue

	@classmethod
	def setConfig(cls, key, value, configType):
		""" Set a specific config key
		"""
		# Check if the key exists in config
		if key not in cls.config:
			cls.config[key] = {}

		# Save the value
		cls.config[key][configType] = value

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
			workingDir = os.path.dirname(workingDir)[0]

		# Check if we found a path
		if path is None:
			path = os.getcwd()

		return os.path.join(path, ".pete", "configuration")

	@classmethod
	def _getLocalPath(cls):
		""" Get the path to the local project configuration files
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
			workingDir = os.path.dirname(workingDir)[0]

		# Check if we found a path
		if path is None:
			path = os.getcwd()

		return os.path.join(path, ".pete", "local")

	@classmethod
	def _getConfigPaths(cls, configTypes):
		""" Get the paths for the config files

			Returns a list
		"""
		# Remember the configs we are going to read
		configs = []

		# Check if we need global config
		if ConfigType.GLOBAL in configTypes:
			# Get the file path
			configs.append({"type": ConfigType.GLOBAL, "path": cls._getGlobalPath()})

		# Check if we need project config
		if ConfigType.PROJECT in configTypes:
			# Get the file path
			configs.append({"type": ConfigType.PROJECT, "path": cls._getProjectPath()})

		# Check if we need local config
		if ConfigType.LOCAL in configTypes:
			# Get the file path
			configs.append({"type": ConfigType.LOCAL, "path": cls._getLocalPath()})

		return configs
