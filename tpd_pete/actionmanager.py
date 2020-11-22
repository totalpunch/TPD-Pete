from .actions.configure import ConfigureAction
from .actions.create_project import CreateProjectAction
from .actions.deploymentaction import DeploymentAction
from .actions.localoverride import SetupLocalOverrideAction


class ActionManager(object):
	@classmethod
	def configure(cls):
		""" Configure TPD Pete
		"""
		return ConfigureAction().start()

	@classmethod
	def createProject(cls, local=False):
		""" Create a new project
		"""
		# Check if this is the local configuation override action
		if local is True:
			return SetupLocalOverrideAction().start()

		return CreateProjectAction().start()

	@classmethod
	def deploy(cls, production=False):
		""" Deploy the current project
		"""
		return DeploymentAction().start(production=production)
