# TPD Pete
![Upload Python Package](https://github.com/totalpunch/TPD-Pete/workflows/Upload%20Python%20Package/badge.svg)

TPD Pete is an AWS Deployment tool for AWS Cloudformation

## Configure

To setup pete use: `pete configure` to setup the default profile and region for AWS

## Usage

To use pete for a project, first set it up using: `pete init`.
This will generate the nessacary files for pete to function.

Then simply use: `pete deploy` to let deploy to your deployment AWS profile.
If you want to deploy to your production environment use: `pete deploy --production`
