import os

from .iaction import IAction
from .deployment.cloudformationdeployment import CloudFormationDeployment
from .deployment.amplifydeployment import AmplifyDeployment
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
			CloudFormationDeployment().start(**kwargs)
			found = True

		# Check if there is an amplify folder
		if os.path.exists("amplify") is True:
			AmplifyDeployment().start(**kwargs)
			found = True

		# Check if we found a deployment option
		if found is False:
			raise Exception("Cant find CloudFormation template: 'template.yaml'")
