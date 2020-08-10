import os
import subprocess
import sys
import tempfile
from enum import Enum

from ..iaction import IAction


class EnvironmentEnum(Enum):
	DEVELOPMENT = "development"
	PRODUCTION = "production"

	def __str__(self):
		return self.value


class IDeploymentAction(IAction):
	""" Interface for Deployment Action
	"""

	def __init__(self):
		""" Init the action
		"""
		# Initialize the parent
		super().__init__()

		# Set the default environment to development
		self.environment = EnvironmentEnum.DEVELOPMENT

	def _createTempDir(self):
		""" Create a temporary directory for deployment

			Returns path
		"""
		# Create the directory
		self.location = tempfile.mkdtemp()

		# Copy all the current files to it
		subprocess.check_call("cp -R %s %s" % (".", self.location), shell=True)

		return self.location

	def _checkDependencies(self):
		""" Check which dependencies we should install
		"""
		# Check NodeJS 'package.json'
		if os.path.exists("package.json") is True:
			subprocess.check_call("npm install --production --ignore-scripts --no-audit --prefix %s" % self.location, shell=True)

		# Check Python 'requirements.txt'
		if os.path.exists("requirements.txt") is True:
			subprocess.check_call("pip install -r requirements.txt -t %s" % self.location, shell=True)

		# Check Python 'poetry.lock'
		if os.path.exists("poetry.lock") is True:
			subprocess.check_call("poetry install", shell=True)
			os.environ["VIRTUAL_ENV"] = os.popen("poetry env info -p").read().strip()

		# Check Python virtualenv
		if os.getenv("VIRTUAL_ENV") is not None:
			packagesPath = os.path.join(os.getenv("VIRTUAL_ENV"), "lib", "python%i.%i" % (sys.version_info[0], sys.version_info[1]), "site-packages")
			subprocess.check_call("cp -R %s/. %s/" % (packagesPath, self.location), shell=True)
