import os
import importlib.util

from termcolor import cprint as print

from .ideploymentaction import IDeploymentAction, EnvironmentEnum
from ...tools.configuration import ConfigurationTool
from ...ihook import IHook


class HookDeployment(IDeploymentAction):
	""" Deployment through Custom hooks
	"""

	def start(self, **kwargs):
		""" Start the deployment
		"""
		# Get the configs
		ConfigurationTool.readConfig()

		# Check if it is the production environment
		if kwargs['production'] is True:
			self.environment = EnvironmentEnum.PRODUCTION

		# Check if there is an hooks directory
		if os.path.exists(".pete/hooks") is False:
			return

		# Read the hook files
		hooks = os.listdir(".pete/hooks")

		# Walk throught the hooks
		for fileName in hooks:
			# Check if it is an py file
			if os.path.splitext(fileName)[1] != ".py":
				continue

			print("Running hook %s" % fileName, "blue")

			# Import the file
			spec = importlib.util.spec_from_file_location(os.path.splitext(fileName)[0], os.path.join(".pete", "hooks", fileName))
			module = importlib.util.module_from_spec(spec)
			spec.loader.exec_module(module)

			# Create a hook
			try:
				hook = module.Hook()
			except AttributeError:
				print("There is no Hook class in %s" % fileName, "red")
				return False

			# Check if it is an IHook
			if isinstance(hook, IHook) is False:
				print("Hook %s is not a IHook subclass" % fileName, "red")
				return False

			# Run the execute
			hook.execute(self.environment)
