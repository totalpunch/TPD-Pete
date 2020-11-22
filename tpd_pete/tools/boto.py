import os
import boto3


class BotoTool(object):
	@classmethod
	def getRegions(cls):
		""" Get all AWS regions
		"""
		# Get a boto client
		client = cls._getClient("ec2", region="us-east-1")

		# Retrieve all the regions
		regions = [region["RegionName"] for region in client.describe_regions()["Regions"]]
		return regions

	@classmethod
	def getRegion(cls, profile):
		""" Get AWS region of a profile
		"""
		# Check if there is an environment var
		if "AWS_DEFAULT_REGION" not in os.environ:
			raise Exception("Could not find a default region, please specify environment variable AWS_DEFAULT_REGION")

		return os.environ["AWS_DEFAULT_REGION"]

	@classmethod
	def getProfiles(cls):
		""" Get all AWS profiles
		"""
		return ["default"]

	@classmethod
	def getS3Buckets(cls, profile=None):
		""" Get your S3 bucket
		"""
		# Get the boto3 client
		client = cls._getClient("s3", region="us-east-1", profile=profile)

		# Retrieve the bucket names
		buckets = client.list_buckets()

		# Get the names
		bucketNames = [bucket["Name"] for bucket in buckets]

		return bucketNames

	@classmethod
	def uploadToS3(cls, fromPath, toBucket, toKey, region, profile=None):
		""" Upload a file to S3
		"""
		# Get a boto3 client
		client = cls._getClient("s3", region=region, profile=profile)

		# Upload the file
		client.upload_file(fromPath, toBucket, toKey)
		return "https://%s.s3.%s.amazonaws.com/%s" % (toBucket, region, toKey)

	@classmethod
	def _getClient(cls, resourceType, region, profile=None):
		""" Get a Boto3 client
		"""
		# Check if the profile name is set
		if profile is not None and profile != "default":
			# Add the profile name to environment variables
			os.environ["AWS_PROFILE"] = profile

		return boto3.client(resourceType, region_name=region)
