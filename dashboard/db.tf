provider "aws" {
    region = "us-west-1"
}

variable "dbpw" {}

resource "aws_db_instance" "dxedb" {
    identifier = "dxedb"
    allocated_storage = 5
    engine = "postgres"
    engine_version = "9.4.5"
    instance_class = "db.t1.micro"
    name = "dxedb"
    username = "frost"
    password = "${var.dbpw}"
    vpc_security_group_ids = ["${aws_security_group.allow_all_db.id}"]
}

resource "aws_security_group" "allow_all_db" {
  name = "allow_all_db"
  description = "Allow all inbound db traffic"

  ingress {
      from_port = 5432
      to_port = 5432
      protocol = "tcp"
      cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
      from_port = 0
      to_port = 0
      protocol = "-1"
      cidr_blocks = ["0.0.0.0/0"]
  }
}

output "host" {
    value = "${aws_db_instance.dxedb.address}"
}
output "port" {
    value = "${aws_db_instance.dxedb.port}"
}
output "username" {
    value = "${aws_db_instance.dxedb.username}"
}
output "database" {
    value = "${aws_db_instance.dxedb.name}"
}
output "password" {
    value = "${var.dbpw}"
}
output "dbstring" {
    value = "postgresql://${aws_db_instance.dxedb.username}:${var.dbpw}@${aws_db_instance.dxedb.address}:${aws_db_instance.dxedb.port}/${aws_db_instance.dxedb.name}"
}
