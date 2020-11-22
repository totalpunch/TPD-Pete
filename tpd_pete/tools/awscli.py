import subprocess
from .boto import BotoTool


class AWSCliTool(object):
	@classmethod
	def getRegion(cls, profile):
		""" Get AWS region of a profile
		"""
		# Check if the AWS Cli is available
		if cls.hasAWSCli() is False:
			# Use boto3
			return BotoTool.getRegion(profile)

		# Open the AWS configuration
		command = "cat ~/.aws/config"

		# Request the config from AWS Cli
		result = subprocess.run(command, shell=True, capture_output=True)

		# Check the response
		if result.returncode != 0:
			raise Exception("Could not successfully get the profiles from AWS Cli. Has you run `aws configure`?")

		# Parse the output
		lines = (result.stdout).decode()

		# Remember the region and profile of the config
		region = None
		configProfile = None

		# Walk throught the lines
		for line in lines.split("\n"):
			# Check line length
			if len(line) == 0:
				continue

			# Check if the next lines belong to a profile
			if line[0] == "[":
				# Save the config profile
				configProfile = line[1:-1]

			# Check if this is the region
			elif line[:6] == "region":
				# Check the profile
				if configProfile == "default" and region is None:
					region = line[9:]
				elif configProfile == profile:
					region = line[9:]

		return region

	@classmethod
	def getProfiles(cls):
		""" Get all AWS profiles
		"""
		# Check if the AWS Cli is available
		if cls.hasAWSCli() is False:
			# Use boto3
			return BotoTool.getProfiles()

		# Build the command
		command = "cat ~/.aws/credentials | grep -o '\[[^]]*\]'"

		# Request all the profiles from AWS Cli
		result = subprocess.run(command, shell=True, capture_output=True)

		# Check the response
		if result.returncode != 0:
			raise Exception("Could not successfully get the profiles from AWS Cli. Has you run `aws configure`?")

		# Parse the output
		output = (result.stdout).decode()

		return [(line[1:-1]).strip() for line in output.split("\n")]

	@classmethod
	def getS3Buckets(cls, profile=None):
		""" Get your S3 bucket
		"""
		# Check if the AWS Cli is available
		if cls.hasAWSCli() is False:
			# Use boto3
			return BotoTool.getS3Buckets(profile)

		# Build the command
		command = "aws s3 ls"

		# Check if there is an profile
		if profile is not None:
			command = command + " --profile %s" % profile

		# Execute the command
		result = subprocess.run(command, shell=True, capture_output=True)

		# Check the response
		if result.returncode != 0:
			raise Exception("Could not successfully get the S3 buckets from AWS Cli. Do you have the right permissions?")

		# Parse the output
		output = (result.stdout).decode()

		return [(line[19:]).strip() for line in output.split("\n")]

	@classmethod
	def hasAWSCli(cls):
		""" Check if the AWS Cli is available
		"""
		# Build the command
		command = "aws help"

		# Request the config from AWS Cli
		result = subprocess.run(command, shell=True, capture_output=True)

		# Check the response
		if result.returncode != 0:
			return False
		return True
