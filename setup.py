from setuptools import setup


setup(
	name="tpd_pete",
	version="0.0.1",
	description="TPD Pete is a AWS Deployment tool for AWS Cloudformation",
	url="https://dev.azure.com/totalpunch/TPD%20Pete",
	author="TotalPunch Development",
	author_email="info@totalpunch.nl",
	license="MIT",
	packages=["tpd_pete"],
	entry_points={
		"console_scripts": [
			"pete = tpd_pete.__main__:main"
		]
	},
	install_requires=[
		"awscli==1.18.31",
		"pyinquirer==1.0.3",
		"halo==0.0.29",
		"termcolor==1.1.0"
	],
	zip_safe=False,
	python_requires=">=3.7",
)
