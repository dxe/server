# Server Build, Deploy, Connect, and Test Server

<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->


- [What's on the server?](#whats-on-the-server)
  - [Cron Jobs](#cron-jobs)
  - [The Chapter Map!](#the-chapter-map)
  - [Facebook Data API Proxy](#facebook-data-api-proxy)
  - [Liberation Pledge Latest Pledgers Proxy](#liberation-pledge-latest-pledgers-proxy)
  - [Attendance App](#attendance-app)
  - [Dashboard Data](#dashboard-data)
- [Background](#background)
  - [Build](#build)
    - [Changing the build](#changing-the-build)
  - [Deploy](#deploy)
    - [Changing the deploy](#changing-the-deploy)
- [Build+Deploy+Connect Process](#builddeployconnect-process)
  - [Build](#build-1)
  - [Deploy](#deploy-1)
  - [Connect](#connect)
    - [Hold up, what ssh-key?](#hold-up-what-ssh-key)
- [Test Locally With Virtualbox and Vagrant](#test-locally-with-virtualbox-and-vagrant)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->


## What's on the server?
### Cron Jobs
See [build/crontab](build/crontab).

* Airtable backup to S3.
* Chapter map data update.
* Facebook to dashboard data dump.

### The Chapter Map!
[A map](http://dxetech.org/maps/chapter_map.html) of all the DxE chapters, pulled
from our activist database.

### Facebook Data API Proxy
A proxy to make a subset of requests to the [Facebook Graph
API](https://developers.facebook.com/docs/graph-api).
[Example.](http://dxetech.org/facebook/attending_event?event_id=122831071398421)

### Liberation Pledge Latest Pledgers Proxy
An endpoint to get the latest pledgers to [The Liberation
Pledge](http://www.liberationpledge.com/). They are stored in a google
spreadsheet, so this uses [Google's Sheet
API](https://developers.google.com/google-apps/spreadsheets/?hl=en) to grab them.
[Example.](http://dxetech.org/pledge/latest_pledgers/2)

### Attendance App
A simple [web page](http://dxetech.org/attend) for organizers to create events and mark who attended it in the airtable database.

### Dashboard Data
Metrics pulled from fb, saved in our db, exposed through the server, and displayed <somewhere>.


## Background
### Setup

Run `make setup` to set up your environment by updating your
submodules

### Build

Run `make build` to build a new image.

We use [packer](https://www.packer.io/intro) to build the AWS AMI
machine image that we're going to deploy. This contains all the
commands and files needed to get the server up to a fully functional
state, Packer basically starts at a base ubuntu image, starts that up
as a an aws instance, uploads the files to the server, installs
software, sets up configuration, powers down the server, then takes a
snapshot of the state before powering down, and saves that.

We can then deploy that image a year later, on different sized instances, maybe
30 at a time, and each will work exactly as the first instance was working before
it was powered down.

#### Changing the build
Edit the file [build/packer.json](build/packer.json). You will likely want to add a step to the
[shell provisioner](https://www.packer.io/docs/provisioners/shell.html), maybe
to `apt-get install` software, or `pip install` python module requirements, or
to `mv` files around. You also may want to add a [file
provisioner](https://www.packer.io/docs/provisioners/file.html) to add files
to the image.


### Deploy

Run `make deploy` to deploy a new image.

We use [terraform](https://terraform.io/) to deploy the image to an
instance. Terraform defines the configuration of the instance, and
interfaces with AWS to deploy it. Terraform doesn't have any way of
detecting what the current state of resources in AWS is. It doesn't
know which servers exist and which don't. The only way it knows is by
storing info on the resources in terraform.tfstate.

It's important to make sure that every time you make a change to the terraform
config, you check in the terraform.tfstate file so in case someone else wants to
make a change, they can have the correct reflection of current resources. The
worst thing that can happen if you mess up is that there can be multiple
versions of the server running at the same time, [costing unecessary
moolah](https://media.giphy.com/media/qbMEvt2tl5flC/giphy.gif). This also means
you need to `git pull` before doing anything with terraform.

#### Changing the deploy
It's unlikely we'll need to do this. However, we may sometimes need to get a bigger
instance, or add another instance, or add ssh keys, To do these things, edit the
file [deploy/deploy.tf](deploy/deploy.tf) and refer to the [terraform docs for
AWS](https://www.terraform.io/docs/providers/aws/).


## Build+Deploy+Connect Process
In order to build and deploy, you need to be authorized to spin up
instances for the build and deploy steps. Running servers costs money,
so that's why you aren't authorized already. The AWS token is stored
in config/aws.sh, and you can add the environmental variables to your
shell by running:

```
. config/aws.sh
```

If you use `make build`, the environmental variables will be set for you.

### Setup

```
make setup
```

Sets up your environment by updating your submodules.


### Build

```
make build
```
Packer will then take a few minutes to build the image, and it will end by
saying something like:
```
--> amazon-ebs: AMIs were created:

us-east-1: ami-xxxxxxxx
```

Then run the following command to copy the image id to the deploy
folder so it's used in the deploy step:

```
make set_image IMAGE=ami-xxxxxxxx
```

### Deploy

First, make sure you've set the image in the `make set_image` step
above. Now to deploy the image, run:

```
make deploy
```

This will run `terraform apply` with the right environmental vars and
output something like:

```
...
Outputs:

  loadbalancer_address   = dxetech-loadbalancer-1251163711.us-east-1.elb.amazonaws.com
```

To undeploy, or destroy, the server and dns record, run:

```
terraform destroy
```

### Connect

You need to get the ip address from AWS. Make sure your
terraform.tfstate file is up to date (`git pull`) and then run the
following to get the ip address of the machine.

```
make get_machine_ip
```

To ssh into the server:
```
ssh ubuntu@<ip address> -i ~/.ssh/dxe_aws_id_rsa
```

There is one reason you should be sshing into the production server:

1. Diagnosing problems with the live server.

If you want to test what commands you need to add to the build process to
add your new feature, bring up a test server and connect to that instead of the
production server. See below for instructions on setting up a test server.

#### Hold up, what ssh-key?

You need do make an ssh key
[(steps 1-2 here)](https://www.digitalocean.com/community/tutorials/how-to-set-up-ssh-keys--2),
name it 'dxe_aws_id_rsa', and add the public key to
`build/conf/authorized_keys`. Then build the image and deploy it.

If you can't afford to redeploy, have someone else ssh in and add the public key
to the end of the file ~/.ssh/authorized_keys. This won't work after the next
deploy unless [deploy.tf](deploy/deploy.tf) is updated as well.

## Test Locally With Virtualbox and Vagrant

You can test the server locally by building it for virtual box. First, install virtualbox and vagrant:

```
On Ubuntu:
$ sudo apt-get install virtualbox-qt virtualbox-guest-additions-iso vagrant
On OS X:
$ brew cask install virtualbox
$ brew cask install vagrant
```

Then run the following to build a virtual box image packaged as a vagrant box:

```
make build-virtualbox
```

Then cd to `vagrant/` and run `vagrant up` to bring up the machine.
Its IP is 192.168.50.4. You can connect to it by going to
http://192.168.50.4 in your browser. You can ssh into it with `vagrant
ssh`. The password is 'ubuntu'.

Basic vagrant commands:

```
vagrant up # start vagrant box
vagrant halt # stop vagrant box
vagrant ssh # ssh into vagrant box
vagrant destroy # destroy vagrant box
```
