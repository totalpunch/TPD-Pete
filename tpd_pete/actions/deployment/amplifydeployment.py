import subprocess

from halo import Halo
from termcolor import cprint as print
from .ideploymentaction import IDeploymentAction


class AmplifyDeployment(IDeploymentAction):
	""" Deployment through AWS Amplify
	"""

	def start(self, **kwargs):
		""" Execute AWS Amplify deployment
		"""
		# Check if it is the production environment
		if kwargs['production'] is False:
			raise Exception("AWS Amplify can only be deployed in production mode")

		# Check the dependencies
		with Halo(text="Installing dependencies") as spinner:
			self._checkDependencies()
			spinner.succeed()

		# Send it to AWS Amplify
		with Halo(text="AWS Amplify deploying") as spinner:
			status = self._amplifyDeploy()
			if status is True:
				spinner.succeed()
			else:
				spinner.fail()
			return status

	def _amplifyDeploy(self):
		""" Deploy with AWS Amplify
		"""
		# List with command to run
		listCommands = ["amplify push", "amplify publish"]

		# Execute the command
		for amplifyCommand in listCommands:
			# Create the command
			command = "cd %s && " % self.location
			command = command + amplifyCommand

			print(command)

			# Run the command
			try:
				subprocess.check_call(command, shell=True)
			except Exception:
				return False
		return True
