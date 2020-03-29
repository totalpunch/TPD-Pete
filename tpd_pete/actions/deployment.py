import sys

from PyInquirer import prompt
from termcolor import cprint as print

from .iaction import IAction
from ..tools.configuration import ConfigurationTool, GlobalConfigurationKey
from ..tools.awscli import AWSCliTool
from ..validator import Validator


class DeploymentAction(IAction):
	""" The deployment action
	"""

	def start(self, **kwargs):
		""" Start the deployment
		"""
		# Get the configs
		globalConfig = ConfigurationTool.readConfig()
		projectConfig = ConfigurationTool.readConfig(project=True)

		#
