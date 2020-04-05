from .actions.configure import ConfigureAction
from .actions.create_project import CreateProjectAction
from .actions.deployment import DeploymentAction

class ActionManager(object):
	@classmethod
	def configure(cls):
		""" Configure TPD Pete
		"""
		return ConfigureAction().start()

	@classmethod
	def createProject(cls):
		""" Create a new project
		"""
		return CreateProjectAction().start()

	@classmethod
	def deploy(cls, production=False):
		""" Deploy the current project
		"""
		return DeploymentAction().start(production=production)
