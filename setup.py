from setuptools import setup, find_packages


setup(
	name="tpd_pete",
	version="0.1.0",
	description="TPD Pete is a AWS Deployment tool for AWS Cloudformation",
	author="TotalPunch Development",
	author_email="info@totalpunch.nl",
	url="https://github.com/totalpunch/TPD-Pete",
	download_url="https://github.com/totalpunch/TPD-Pete/archive/0.1.0.tar.gz",
	license="MIT",
	packages=find_packages(),
	entry_points={
		"console_scripts": [
			"pete = tpd_pete.__main__:main"
		]
	},
	install_requires=[
		"awscli==1.18.31",
		"pyinquirer==1.0.3",
		"halo==0.0.29",
		"termcolor==1.1.0",
		"cfn_flip==1.2.2"
	],
	zip_safe=False,
	python_requires=">=3.7"
)
