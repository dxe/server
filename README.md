#Server Build, Deploy, Connect, and Test Server

<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
<!-- **Table of Contents**  *generated with [DocToc](https://github.com/thlorenz/doctoc)* -->

- [What's on the server?](#whats-on-the-server)
  - [Cron jobs](#cron-jobs)
  - [The chapter map!](#the-chapter-map)
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
- [Test Server](#test-server)
- [Test Subdomain](#test-subdomain)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->



##What's on the server?
###Cron jobs
See [build/crontab](build/crontab).

* Airtable backup to S3.
* Chapter map data update.

###The chapter map!
[A map](http://dxetech.org/maps/chapter_map.html) of all the DxE chapters, pulled
from our activist databsae.



##Background
###Build
We use [packer](https://www.packer.io/intro) to build the DigitalOcean
machine image that we're going to deploy. This contains all the commands and
files needed to get the server up to a fully functional state, Packer basically
starts at a base ubuntu image, starts that up as a
a [droplet](https://www.digitalocean.com/community/tutorials/how-to-create-your-first-digitalocean-droplet-virtual-server)(server),
uploads the files to the server, installs software, sets up configuration,
powers down the server, then takes a snapshot of the state before powering down,
and saves that.

We can then deploy that image a year later, on different sized droplets, maybe
30 at a time, and each will work exactly as the first droplet was working before
it was powered down.

####Changing the build
Edit the file [build/packer.json](build/packer.json). You will likely want to add a step to the
[shell provisioner](https://www.packer.io/docs/provisioners/shell.html), maybe
to `apt-get install` software, or `pip install` python module requirements, or
to `mv` files around. You also may want to add a [file
provisioner](https://www.packer.io/docs/provisioners/file.html) to add files
to the image.


###Deploy
We use [terraform](https://terraform.io/) to deploy the image to a droplet.
Terraform defines the configuration of the droplet, and interfaces with
DigitalOcean to deploy it.  Terraform doesn't have any way of detecting
what the current state of resources in DigitalOcean is. It doesn't know
which servers exist and which don't. The only way it knows is by storing
info on the resources in terraform.tfstate.

It's important to make sure that every time you make a change to the terraform
config, you check in the terraform.tfstate file so in case someone else wants to
make a chagne, they can have the correct reflection of current resources. The
worst thing that can happen if you mess up is that there can be multiple
versions of the server running at the same time, [costing unecessary
moolah](https://media.giphy.com/media/qbMEvt2tl5flC/giphy.gif). This also means
you need to `git pull` before doing anything with terraform.

####Changing the deploy
It's unlikely we'll need to do this. However, we may sometimes need to get a bigger
droplet, or add another droplet, or add ssh keys, To do these things, edit the
file [deploy/deploy.tf](deploy/deploy.tf) and refer to the [terraform docs for
DigitalOcean
Droplets](https://www.terraform.io/docs/providers/do/r/droplet.html).


##Build+Deploy+Connect Process
In order to build and deploy, you need to be authorized to spin up droplets for
the build and deploy steps. Running servers costs money, so that's why you aren't
authorized already. Get the fancy shmancy DigitalOcean Personal Access
token from someone else, and add this to your .bashrc (BUT NOT IF YOU KEEP THAT
IN VERSION CONTROL):
```
export DIGITALOCEAN_API_TOKEN=<the token you were given> # for packer
export DIGITALOCEAN_TOKEN=$DIGITALOCEAN_API_TOKEN # for terraform
```

###Build
```
packer build build/packer.json
```
Packer will then take a few minutes to build the image, and it will end by
saying something like:
```
--> digitalocean: A snapshot was created: 'dxe-image-1441861986' in region 'sfo1'
```
Copy that image name for the deploy step.

###Deploy
```
cd deploy/
```

Since DigitalOcean doesn't allow referring to images by their name,
we have to do this silly step of getting the image id from the image name.
Fortunately, code has been written to save you most of the annoyance. Get the
image id from the name by running:

```
pip install -r requirements.txt #install python module requirements for the script
python get_image_id.py <image name>
```

This will output the image id. Copy that. Then open [deploy.tf](deploy/deploy.tf)
, go to the line that says "image_id". Replace the value there with the image id
you just copied. Now to deploy the image, run:

```
terraform apply
```

This will output something like:
```
...
Outputs:
  ip = <ip address>
```

To undeploy, or destroy, the server and dns record, run:

```
terraform destroy
```

###Connect
To ssh into the server:
```
ssh root@<ip address> -i ~/.ssh/dxe_do_id_rsa
```

There is one reason you should be sshing into the production server:

1. Diagnosing problems with the live server.

If you want to test what commands you need to add to the build process to
add your new feature, bring up a test server and connect to that instead of the
production server. See below for instructions on setting up a test server.

####Hold up, what ssh-key?
You need do make an ssh
key [(steps 1-3 here)](https://www.digitalocean.com/community/tutorials/how-to-set-up-ssh-keys--2),
name it 'dxe_do_id_rsa', and give the public key to someone else to add to
DigitalOcean. Get the ssh key fingerprint either from that person, or by
running:
```
ssh-keygen -lf ~/.ssh/dxe_do_id_rsa
```

The last step to be able to ssh into the server is to add that fingerprint to
the [deploy/deploy.tf](deploy/deploy.tf) terraform config file and redeploy.

If you can't afford to redeploy, have someone else ssh in and add the public key
to the end of the file ~/.ssh/authorized_keys. This won't work after the next
deploy unless [deploy.tf](deploy/deploy.tf) is updated as well.


##Test Server
Before trying to do this, please read the Background section. That will give you
more context to understand how this works.

We want to bring up a server that you can play around with without disturbing
the production server. All of the above steps are the same with the exception of
the deploy step. Terraform keeps its knowledge of the production server in the
[terraform.tfstate](deploy/terraform.tfstate) file. If we made a change to
[deploy.tf](deploy/deploy.tf) and then ran `terraform apply`, it would bring
down the production server, and bring a new one up with your changes. We
don't want that, we want to leave production alone and bring up another server.

First, so you don't forget that this is a test server and not the produciton
server, run:

```
mv deploy test_deploy
```

To tell terraform to forget about the production server, run:

```
cd test_deploy/
rm terraform.tfstate*
```

To tell ferraform not to change the DNS record (that points dxetech.org to the
production server ip), run:

```
rm dns.tf
```

Finally, edit deploy.tf and change the server name from `"dxetech-server-production"`
to `"dxetech-server-test"` so it's easy to see on the digitalocean console that
the server is a test server, and not prodcution.

Now we're all set to deploy the test server, so run:

```
terraform apply
```

Since it costs money to keep servers up, when you're not actively using/testing it,
please bring down the server with:

```
terraform deploy
```

It's not much money so don't be paranoid or inconvenience yourself for that
reason, but be conscious.

##Test Subdomain

In some situations, testing requires a server has a domain instead of just an IP
address. We can use a subdomain on dxetech.org to do that, which usually
suffices. Make a file `testdns.tf` in test_deploy/, and make this its contents:

```
resource "digitalocean_record" "test" {
    domain = "dxetech.org"
    type = "A"
    name = "test"
    value = "${digitalocean_droplet.server.ipv4_address}"
}
```

Terraform considers this dns record to be a "resource" like the server, so when
you run `terraform apply` and `terraform destroy`, terraform will create and
destroy the dns subdomain record.

Hurray! Now [test.dxetech.org](test.dxetech.org) points at your test server! <3
