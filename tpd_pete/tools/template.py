import json
from enum import Enum, auto as autoEnum


from cfn_tools import load_yaml, dump_json


class DevSuffixEnum(Enum):
	ITEM_NAME = autoEnum()


class TemplateTool(object):
	DEV_SUFFIX_TYPES = {
		"AWS::Lambda::Function": DevSuffixEnum.ITEM_NAME,
		"AWS::DynamoDB::Table": "TableName",
		"AWS::AppSync::GraphQLApi": "Name",
		"AWS::IAM::Role": DevSuffixEnum.ITEM_NAME
	}

	NO_TYPE_TAGS_SUPPORT = [
		"AWS::AppSync::GraphQLSchema",
		"AWS::AppSync::DataSource",
		"AWS::AppSync::Resolver",
		"AWS::IAM::Role",
		"AWS::Events::Rule",
		"AWS::Lambda::Permission"
	]

	@classmethod
	def parseTemplate(cls, templateContent):
		""" Change the YAML templateContent to a plain JSON format
		"""
		# Read the YAML content
		templateContent = load_yaml(templateContent)

		# Change to JSON
		templateContent = dump_json(templateContent)

		return json.loads(templateContent)

	@classmethod
	def addSuffixToItems(cls, templateContent):
		""" Add the suffix to the items in the templateContent
		"""
		# Walk through all the items
		for itemName in (list((templateContent['Resources']).keys())):
			# Get the information
			itemType = templateContent['Resources'][itemName]['Type']

			# Check if we now what to change
			if itemType in cls.DEV_SUFFIX_TYPES:
				# Check if we change the name of the item
				if cls.DEV_SUFFIX_TYPES[itemType] == DevSuffixEnum.ITEM_NAME:
					newItemName = itemName + "Dev"
					templateContent['Resources'][newItemName] = templateContent['Resources'][itemName]
					del templateContent['Resources'][itemName]

				# Change the mentioned thing
				else:
					templateContent['Resources'][itemName]['Properties'][cls.DEV_SUFFIX_TYPES[itemType]] = templateContent['Resources'][itemName]['Properties'][cls.DEV_SUFFIX_TYPES[itemType]] + "_DEV"

			# Just try it
			else:
				if "Name" in templateContent['Resources'][itemName]['Properties']:
					templateContent['Resources'][itemName]['Properties']['Name'] = templateContent['Resources'][itemName]['Properties']['Name'] + "_DEV"
				elif "Id" in templateContent['Resources'][itemName]['Properties']:
					templateContent['Resources'][itemName]['Properties']['Id'] = templateContent['Resources'][itemName]['Properties']['Id'] + "_DEV"
				else:
					raise Exception("I dont know how to change the name of this item '%s'" % itemName)

		return templateContent

	@classmethod
	def addTagsToItems(cls, templateContent):
		""" Add tags to each resource in the templateContent
		"""
		# Walk through all the items
		for itemName in (list((templateContent['Resources']).keys())):
			# Get the information
			itemType = templateContent['Resources'][itemName]['Type']

			# Check if we should add the tags
			if itemType in cls.NO_TYPE_TAGS_SUPPORT:
				continue

			# Check if tags already exists
			if "Tags" not in templateContent['Resources'][itemName]['Properties']:
				templateContent['Resources'][itemName]['Properties']['Tags'] = []

			# Get the key names
			keyNames = [tag['Key'] for tag in templateContent['Resources'][itemName]['Properties']['Tags']]

			# Add the name tag
			if "Name" not in keyNames:
				(templateContent['Resources'][itemName]['Properties']['Tags']).append({"Key": "Name", "Value": itemName})

			# Add the environment tag
			if "Environment" not in keyNames:
				(templateContent['Resources'][itemName]['Properties']['Tags']).append({"Key": "Environment", "Value": {"Ref":  "environment"}})

			# Add the stack tag
			if "Stack" not in keyNames:
				(templateContent['Resources'][itemName]['Properties']['Tags']).append({"Key": "Stack", "Value": {"Ref":  "stackName"}})

			# Add the project tag
			if "Project" not in keyNames:
				(templateContent['Resources'][itemName]['Properties']['Tags']).append({"Key": "Project", "Value": {"Ref":  "projectName"}})

		return templateContent

	@classmethod
	def checkVariables(cls, templateContent):
		""" Check if all the required variables are added
		"""
		# Remember all the parameters
		parameters = {}

		# Check if there are parameters
		if "Parameters" not in templateContent:
			templateContent['Parameters'] = {}

		# Check if all exists
		if "s3FileName" not in templateContent['Parameters']:
			templateContent['Parameters']['s3FileName'] = {"Type": "String"}
		if "environment" not in templateContent['Parameters']:
  			templateContent['Parameters']['environment'] = {"Type": "String"}
		if "deploymentBucket" not in templateContent['Parameters']:
			templateContent['Parameters']['deploymentBucket'] = {"Type": "String"}
		if "stackName" not in templateContent['Parameters']:
			templateContent['Parameters']['stackName'] = {"Type": "String"}
		if "projectName" not in templateContent['Parameters']:
			templateContent['Parameters']['projectName'] = {"Type": "String"}

		# Check for other parameters
		for parameterName in templateContent['Parameters']:
			# Check if this is an Pete parameter
			if parameterName in ["s3FileName", "environment", "deploymentBucket", "stackName", "projectName"]:
				continue

			# Get the type of parameter
			parameterType = "String"
			if "Type" in templateContent['Parameters'][parameterName]:
				parameterType = templateContent['Parameters'][parameterName]['Type']

			# Save the parameter
			parameters[parameterName] = parameterType

		return (templateContent, parameters)
