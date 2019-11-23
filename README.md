# snapshotanalyzer
Demo project for AWS EC2 instance snapshots

## About

This is a project demo, and uses boto3 to manage AWS EC2 instance snapshots.

## Configuring

shotty users the configuration file created by the AWS cli. e.g.

'aws configure --profile shotty'

## Running

pipenv run python shotty/shotty.py <command> --project=<project name>

*commands for instances* list, start, stop
*commands for volumes* vlist
*commands for snapshots* slist, snapshot
*project* depends on your project name
