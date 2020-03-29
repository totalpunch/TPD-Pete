import subprocess


class AWSCliTool(object):
	@classmethod
	def getProfiles(cls):
		""" Get all AWS profiles
		"""
		# Build the command
		command = "cat ~/.aws/credentials | grep -o '\[[^]]*\]'"

		# Request all the profiles from AWS Cli
		result = subprocess.run(command, shell=True, capture_output=True)

		# Check the response
		if result.returncode != 0:
			raise Exception("Could not successfully get the profiles from AWS Cli. Has you run `aws configure`?")

		# Parse the output
		output = (result.stdout).decode()

		return [line[1:-1] for line in output.split("\n")]

	@classmethod
	def getS3Buckets(cls, profile=None):
		""" Get your S3 bucket
		"""
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

		return [line[19:] for line in output.split("\n")]
