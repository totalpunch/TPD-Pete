# TPD Pete
[![PyPI version fury.io](https://badge.fury.io/py/tpd-pete.svg)](https://pypi.python.org/pypi/tpd-pete/)
![Upload Python Package](https://github.com/totalpunch/TPD-Pete/workflows/Upload%20Python%20Package/badge.svg)
![Lint](https://github.com/totalpunch/TPD-Pete/workflows/Lint/badge.svg)

TPD Pete is an AWS Deployment tool for AWS Cloudformation

## Configure

To setup pete use: `pete configure` to setup the default profile and region for AWS

## Usage

To use pete for a project, first set it up using: `pete init`.
This will generate the nessacary files for pete to function.

Then simply use: `pete deploy` to let deploy to your deployment AWS profile.
If you want to deploy to your production environment use: `pete deploy --production`

If you have multiple collaborators on a project, and you dont want to share the same development environment.
Then you could also use `pete init --local` to setup some development override for you locally.
These will be used instead of the project development environment setup, if this has been setup.

So if you dont have local overrides, it uses the project config.
If you dont have a project config, it uses the global config which is specific to you.
You can save which account, region or bucket to use for a project in the project config.
This will be saved in the `.pete` folder in you project folder.
You should add this file to your VCS (like Git or SVN).
But not the `local` file inside that folder, which hold the local overrides.
