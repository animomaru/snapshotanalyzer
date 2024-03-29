#import part - imports functions/modules needed for the project
import boto3
import botocore
import click

#initialised variables for the Project
session = boto3.Session(profile_name = 'shotty')
ec2 = session.resource('ec2')

#filters the instances
def filter_instances(project):
    #create a blank list
    instances = []

    #checks if the project value is true
    if project:
        #this is another dictionary, that checks out the project and tag from EC2 console
        filters = [{'Name':'tag:Project', 'Values':[project]}]
        #gets the project/tag and assign to variable instances
        instances = ec2.instances.filter(Filters=filters)
    else:
        #returns all instances if project parameter used is not available
        instances = ec2.instances.all()

    return instances

def has_pending_snapshot(volume):
    snapshots = list(volume.snapshots.all())
    return snapshots and snapshots[0].state == 'pending'

###########################################
##### SNAPSHOTS #####
###########################################

@click.group('snapshots')
def snapshots():
    """Commands for snapshots"""

@snapshots.command('slist')
@click.option('--project', default=None,
    help="Only snapshots for project (tag Project:<name>)")
@click.option('--all', 'list_all', default=False, is_flag=True,
    help="List all snapshots for each volume (tag Project:<name>)")

#function definition for the script
#must define the project/tag name to run the function
def list_snapshots(project, list_all):
    #python text list_volumes
    "List EC2 snapshots"

    instances = filter_instances(project)

    for i in instances:
        for v in i.volumes.all():
            for s in v.snapshots.all():
                print(", ".join((
                s.id,
                v.id,
                i.id,
                s.state,
                s.progress,
                s.start_time.strftime("%c")
                )))

                if s.state == 'completed' and not list_all: break
    return


###########################################
##### VOLUMES #####
###########################################

#click functions - wraps the functions - volumes
@click.group('volumes')
def volumes():
    """Commands for volumes"""

@volumes.command('vlist')
@click.option('--project', default=None,
    help="Only volumes for project (tag Project:<name>)")

#function definition for the script
#must define the project/tag name to run the function
def list_volumes(project):
    #python text list_volumes
    "List EC2 volumes"

    instances = filter_instances(project)

    for i in instances:
        for v in i.volumes.all():
            print(", ".join((
            v.id,
            i.id,
            v.state,
            str(v.size) + "GB",
            v.encrypted and "Encrypted" or "Not Encrypted"
            )))

    return

###########################################
##### INSTANCES #####
###########################################

#click functions - wraps the functions - instances
@click.group('instances')
def instances():
    """Commands for instances"""

###########################################
#beginning of the 'list' command
###########################################

@instances.command('snapshot', help="Create snapshots of all volumes")
@click.option('--project', default=None,
    help="Only instances for project (tag Project:<name>)")

def create_snapshots(project):
    "Create snapshots for EC2 instances"

    instances = filter_instances(project)

    for i in instances:
        print("Stopping {0}....".format(i.id))
        i.stop()
        i.wait_until_stopped()
        for v in i.volumes.all():
            if has_pending_snapshot(v):
                print(" Skipping {0}".format(v.id))
                continue
            print("Creating snapshot of {0}".format(v.id))
            v.create_snapshot(Description="Created by Shotty")
        print("Starting {0}....".format(i.id))
        i.start()
        i.wait_until_running()

    print("Snapshots Created Successfully!")
    return

@instances.command('list')
@click.option('--project', default=None,
    help="Only instances for project (tag Project:<name>)")

#function definition for the script
#must define the project/tag name to run the function
def list_instances(project):
    #python text list_instances
    "List EC2 Instances"

    instances = filter_instances(project)

    #gets all the instances and return to the screen
    for i in instances:
        #gets the tag value for each of the instances
        tags = { t['Key']: t['Value'] for t in i.tags or [] }
        print(', '.join((
        i.id,
        i.instance_type,
        i.placement['AvailabilityZone'],
        i.state['Name'],
        i.public_dns_name,
        tags.get('Projects', '<no project>')
        )))

    return

###########################################
#beginning of the 'stop' command
###########################################

@instances.command('stop')
@click.option('--project', default=None,
    help="Only instances for project (tag Project:<name>)")

def stop_instances(project):

        "Stop EC2 Instances"

        instances = filter_instances(project)

        for i in instances:
            print("Stopping {0}...".format(i.id))
            try:
                i.stop()
            except botocore.exceptions.ClientError as e:
                print(" Could not stop {0}.".format(i.id) + str(e))
                continue

        return

###########################################
#beginning of the 'start' command
###########################################

@instances.command('start')
@click.option('--project', default=None,
    help="Only instances for project (tag Project:<name>)")

def start_instances(project):
        "Start EC2 Instances"

        instances = filter_instances(project)

        for i in instances:
            print("Starting {0}...".format(i.id))
            try:
                i.start()
            except botocore.exceptions.ClientError as e:
                print(" Could not start {0}.".format(i.id) + str(e))
                continue

        return

cli = click.CommandCollection(sources=[snapshots, volumes, instances])

if __name__ == '__main__':
    cli()
