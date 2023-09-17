locals {
  instances = flatten([
    for srv in var.configuration : [
      {
        instance_name = srv.name
        instance_type = srv.type
        subnet_id     = "subnet-04f8acc1bfde8ebb0"
        ami_id        = srv.ami_id
      }
    ]
  ])
}

resource "aws_instance" "server" {
  for_each = { for server in local.instances : server.instance_name => server }

  ami           = each.value.ami_id
  instance_type = each.value.instance_type
  subnet_id     = each.value.subnet_id
  tags = {
    Name = each.value.instance_name
  }
}
