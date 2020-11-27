import os
import sys
from termcolor import cprint as print

from .iaction import IAction
from .deployment.cloudformationdeployment import CloudFormationDeployment
from .deployment.amplifydeployment import AmplifyDeployment
from .deployment.zappadeployment import ZappaDeployment
from .deployment.ideploymentaction import EnvironmentEnum


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
		# Remember if we found a deployment option
		found = False

		# Check if there is an template
		if os.path.exists("template.yaml") is True:
			print("Starting CloudFormation deployment", "blue")
			CloudFormationDeployment().start(**kwargs)
			found = True

		# Check if there is an amplify folder
		if os.path.exists("amplify") is True:
			print("Starting Amplify deployment", "blue")
			AmplifyDeployment().start(**kwargs)
			found = True

		# Check if there is an zappa folder
		if os.path.exists("zappa_settings.json") is True:
			print("Starting Zappa deployment", "blue")
			ZappaDeployment().start(**kwargs)
			found = True

		# Check if we found a deployment option
		if found is False:
			print("Could not find any supported deployment methodes. Use Amplify, CloudFormation or Zappa", "red")
			sys.exit(1)
