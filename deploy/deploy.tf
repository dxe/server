variable "config" {
    default ={
        "server_name" = "dxetech-server-production"
        "mperrone_ssh_print" = "b6:c7:cf:30:3c:fb:ff:a8:73:d1:75:c8:3b:e4:fe:2d"
        "lmz_ssh_print" = "18:99:7d:3a:e0:e7:a6:99:ce:0e:eb:ed:a8:63:78:41"
        "image_id" = ""
    }
}

provider "aws" {
    region = "us-east-1"
}

resource "aws_elb" "server" {
    name = "dxetech-loadbalancer"

    tags {
        Name = "dxetech-loadbalancer"
    }
    subnets = ["subnet-3d0c6216"]
    security_groups = ["sg-ceb760a9"]

    listener {
        instance_port = 80
        instance_protocol = "http"
        lb_port = 80
        lb_protocol = "http"
    }

    listener {
        instance_port = 80
        instance_protocol = "http"
        lb_port = 443
        lb_protocol = "https"
        ssl_certificate_id = "arn:aws:acm:us-east-1:030824242463:certificate/13efadd3-195c-4cca-88e5-d62aadda8ed5"
    }

    health_check {
        healthy_threshold = 2
        unhealthy_threshold = 2
        timeout = 5
        interval = 10
        target = "TCP:80"
    }

    cross_zone_load_balancing = false
    idle_timeout = 60
    connection_draining = true
    connection_draining_timeout = 400
}

resource "aws_launch_configuration" "server" {
    lifecycle { create_before_destroy = true }

    image_id = "${var.config.image_id}"
    instance_type = "t2.micro"
    key_name = "xps15key"
    security_groups = ["sg-ceb760a9"]
}

resource "aws_autoscaling_group" "server" {
    lifecycle { create_before_destroy = true }
    name = "dxetech - ${aws_launch_configuration.server.name}"
    min_size = 1
    max_size = 1
    launch_configuration = "${aws_launch_configuration.server.name}"
    load_balancers = ["${aws_elb.server.id}"]
    vpc_zone_identifier = ["subnet-3d0c6216"]

    tag {
        key = "Name"
        value = "${var.config.server_name}"
        propagate_at_launch = true
    }
}

output "loadbalancer_address" {
    value = "${aws_elb.server.dns_name}"
}
