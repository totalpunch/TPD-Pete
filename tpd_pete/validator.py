import os
import subprocess

from .tools.configuration import ConfigurationTool


class Validator(object):
	@classmethod
	def findCloudformationTemplate(cls):
		""" Search for an Cloudformation Template

			Returns path to template
		"""
		pass

	@classmethod
	def findPeteRoot(cls):
		""" Search for a TPD Pete enabled folder

			Returns path to root
		"""
		pass

	@classmethod
	def hasAWSCli(cls):
		""" Check if AWS cli is available
		"""
		try:
			subprocess.check_call(["aws", "help"], shell=True)
		except Exception:
			return False
		return True

	@classmethod
	def hasPeteSetup(cls):
		""" Check if pete configure has been run
		"""
		# Check the path
		path = ConfigurationTool.getGlobalPath()

		# Check if the path exists
		if os.path.exists(path) is False:
			return False
		return True
