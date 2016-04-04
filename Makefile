.PHONY: setup build build-virtualbox deploy set_image get_machine_ip

setup:
	git submodule update --init
# Download packer if it isn't installed.
	hash packer &> /dev/null || echo "Download packer: https://www.packer.io/downloads.html"
# Download terraform if it isn't installed.
	hash terraform &> /dev/null || echo "Download terraform: https://www.terraform.io/downloads.html"

build:
	. config/aws.sh && packer build -only=amazon-ebs build/packer.json

build-virtualbox:
	packer build -only=virtualbox-iso build/packer.json

set_image:
	cd deploy && ./write_image_id.sh $(IMAGE)

deploy:
	. config/aws.sh && cd deploy && terraform apply

get_machine_ip:
	. config/aws.sh && cd deploy && ./get_machine_ip.py
