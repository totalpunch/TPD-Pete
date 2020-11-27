import sys

from PyInquirer import prompt
from termcolor import cprint as print

from ..tools.awscli import AWSCliTool


class IAction(object):
	def start(self, **kwargs):
		pass

	def _askAWSProfile(self, default=None):
		""" Ask for an AWS Profile
		"""
		# Get all the profile from AWS Cli
		profiles = AWSCliTool.getProfiles()

		# Check if there are profile
		if len(profiles) == 0:
			raise Exception("To use Pete, first setup AWS Cli by using: `aws configure`")

		# Ask the question
		answer = prompt({
			"type": "list",
			"name": "profile",
			"choices": profiles,
			"message": "Which profile do you want to use?",
			"default": default if default is not None else ""
		})

		# Check if there is an answer
		if answer == {}:
			sys.exit()

		return answer['profile']

	def _askS3Bucket(self, profile, default=None):
		""" Ask for an S3 Bucket
		"""
		# Get all the profile from AWS Cli
		buckets = AWSCliTool.getS3Buckets(profile=profile)

		# Check if there are buckets
		if len(buckets) == 0:
			print("Could not get your S3 bucket, either because you have none or because you dont have permission.", "red")
			print("Enter the name of the S3 bucket you would like to use.", "yellow")
			return self._askName()

		# Ask the question
		answer = prompt({
			"type": "list",
			"name": "bucket",
			"choices": buckets,
			"message": "Which bucket do you want to use?",
			"default": default if default is not None else ""
		})

		# Check if there is an answer
		if answer == {}:
			sys.exit()

		return answer['bucket']

	def _askName(self, default=None):
		""" Ask for a name
		"""
		# Ask the question
		answer = prompt({
			"type": "input",
			"name": "name",
			"message": "What name do you want to use?",
			"default": default if default is not None else ""
		})

		# Check if there is an answer
		if answer == {}:
			sys.exit()

		return answer['name']

	def _askAWSRegion(self, profile, default=None):
		""" Ask to override AWS region
		"""
		# Get the default region
		defaultRegion = AWSCliTool.getRegion(profile)

		# Ask to override the region
		answer = prompt({
			"type": "confirm",
			"name": "override",
			"message": "Do you want to override the default region (%s)?" % defaultRegion,
			"default": True if default is not None else False
		})

		# Check if there is an answer
		if answer == {}:
			sys.exit()

		# Check the answer
		if answer['override'] is False:
			return None

		# Ask for the region
		answer = prompt({
			"type": "input",
			"name": "region",
			"message": "What region do you want to use?",
			"default": default if default is not None else ""
		})

		# Check if there is an answer
		if answer == {}:
			sys.exit()

		return answer['region']

	def _askOverride(self, default=False):
		""" Ask if you want to override
		"""
		# Ask the question
		answer = prompt({
			"type": "confirm",
			"message": "Do you want to override?",
			"name": "override",
			"default": default if default is not None else ""
		})

		# Check if there is an answer
		if answer == {}:
			sys.exit()

		return answer['override']

	def _askConfirm(self, message, default=False):
		""" Ask if you want to confirm
		"""
		# Ask the question
		answer = prompt({
			"type": "confirm",
			"message": message,
			"name": "confirm",
			"default": default if default is not None else ""
		})

		# Check if there is an answer
		if answer == {}:
			sys.exit()

		return answer['confirm']
