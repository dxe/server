.PHONY: build deploy set_image get_machine_ip

build:
	. config/aws.sh && packer build build/packer.json

set_image:
	cd deploy && ./write_image_id.sh $(IMAGE)

deploy:
	. config/aws.sh && cd deploy && terraform apply

get_machine_ip:
	. config/aws.sh && cd deploy && ./get_machine_ip.py
