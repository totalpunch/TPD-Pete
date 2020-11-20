import os
from setuptools import setup, find_packages
import tpd_pete


# Read the contents of the README file
folderPath = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(folderPath, "README.md"), encoding="utf-8") as f:
	longDescription = f.read()


# Generate setup config
setup(
	name="tpd_pete",
	version=tpd_pete.VERSION,
	description="TPD Pete is a AWS Deployment tool for AWS Cloudformation",
	author="TotalPunch Development",
	author_email="info@totalpunch.nl",
	url="https://github.com/totalpunch/TPD-Pete",
	download_url="https://github.com/totalpunch/TPD-Pete/archive/%s.tar.gz" % tpd_pete.VERSION,
	license="MIT",
	packages=find_packages(),
	entry_points={
		"console_scripts": [
			"pete = tpd_pete.__main__:main"
		]
	},
	install_requires=[
		"boto3==1.16.22",
		"pyinquirer==1.0.3",
		"halo==0.0.29",
		"termcolor==1.1.0",
		"cfn_flip==1.2.2"
	],
	zip_safe=False,
	python_requires=">=3.7",
	long_description=longDescription,
	long_description_content_type="text/markdown"
)
