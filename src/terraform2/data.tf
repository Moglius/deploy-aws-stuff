data "aws_ami" "selected_ami" {
  for_each = { for server in local.instances : server.instance_name => server }

  most_recent = true

  filter {
    name   = "name"
    values = ["${each.value.ami_filter}*"]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }

  filter {
    name   = "architecture"
    values = ["x86_64"]
  }

}
