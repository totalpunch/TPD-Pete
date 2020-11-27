import os
import sys
from termcolor import cprint as print

from .iaction import IAction
from .deployment.cloudformationdeployment import CloudFormationDeployment
from .deployment.amplifydeployment import AmplifyDeployment
from .deployment.hookdeployment import HookDeployment
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
		error = False

		# Check if there is an template
		if os.path.exists("template.yaml") is True:
			print("Starting CloudFormation deployment", "blue")
			result = CloudFormationDeployment().start(**kwargs)
			if result is False:
				error = True
			found = True

		# Check if there is an amplify folder
		if os.path.exists("amplify") is True:
			print("Starting Amplify deployment", "blue")
			result = AmplifyDeployment().start(**kwargs)
			if result is False:
				error = True
			found = True

		# Check if there is an zappa folder
		if os.path.exists("zappa_settings.json") is True:
			print("Starting Zappa deployment", "blue")
			result = ZappaDeployment().start(**kwargs)
			if result is False:
				error = True
			found = True

		# Check if there are any custom hooks
		if os.path.exists(".pete/hooks") is True:
			print("Starting Custom hooks deployment", "blue")
			result = HookDeployment().start(**kwargs)
			if result is False:
				error = True
			found = True

		# Check if we found a deployment option
		if found is False:
			print("Could not find any supported deployment methodes. Use Amplify, CloudFormation or Zappa", "red")
			sys.exit(1)

		# Check if an error occured
		if error is True:
			# Set the exit code
			sys.exit(1)
