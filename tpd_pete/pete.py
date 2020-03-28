import argparse


class Pete(object):
	""" TPD Pete
	"""

	def __init__(self):
		pass

	def start(self):
		""" Start TPD Pete
		"""
		# Create an argument parser
		parser = argparse.ArgumentParser(prog="pete", description="TPD Pete is an AWS deployment tool for AWS Cloudformation")
		parser.add_argument("mode", choices=["init", "deploy", "configure"], help="Select a mode")
		parser.add_argument("--production", help="Deploy a project to your production AWS profile", )

		# Create a argparse group with the modes
		modeGroup = parser.add_argument_group("Choices of modes")
		modeGroup.add_argument("configure", help="Setup your TPD Pete")
		modeGroup.add_argument("init", help="Create a new project")
		modeGroup.add_argument("deploy", help="Deploy to AWS Cloudformation")

		# Parse the arguments
		args = parser.parse_args()

		# Check the result
		if args.mode == "configure":
			pass
		elif args.mode == "init":
			pass
		elif args.mode == "deploy":
			if args.production:
				pass
			else:
				pass

