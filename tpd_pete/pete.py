import argparse
import platform

from .actionmanager import ActionManager
from .validator import Validator


class Pete(object):
	""" TPD Pete
	"""

	def __init__(self):
		# Check if Linux
		if platform.system() != "Linux":
			raise Exception("This can only be used on Linux machines")

	def start(self):
		""" Start TPD Pete
		"""
		# Create an argument parser
		parser = argparse.ArgumentParser(prog="pete", description="TPD Pete is an AWS deployment tool for AWS Cloudformation")
		parser.add_argument("mode", choices=["configure", "init", "deploy"], help="Select a mode")
		parser.add_argument("--production", help="Deploy a project to your production AWS profile", action="store_true")
		parser.add_argument("--local", help="Override project setup with local development overrides", action="store_true")

		# Create a argparse group with the modes
		# modeGroup = parser.add_argument_group("Choices of modes")
		# modeGroup.add_argument("configure", help="Setup your TPD Pete")
		# modeGroup.add_argument("init", help="Create a new project")
		# modeGroup.add_argument("deploy", help="Deploy to AWS Cloudformation")

		# Parse the arguments
		args = parser.parse_args()

		# Check if we used the configure mode
		if args.mode == "configure":
			return ActionManager.configure()

		# Check if we have a global configured Pete
		if Validator.hasPeteSetup() is False:
			raise Exception("Error: You need to setup Pete first! Use the configure mode, to setup Pete.")

		# Check if we used the init mode
		if args.mode == "init":
			return ActionManager.createProject(local=args.local)

		# Check if we have a project configured Pete
		if Validator.hasPeteProjectSetup() is False:
			raise Exception("Error: You need to init the project first! Use the init mode, to create a project of Pete.")

		# Check if we used the deploy mode
		if args.mode == "deploy":
			return ActionManager.deploy(production=args.production)
