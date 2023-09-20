locals {
  instances = flatten([
    for srv in var.configuration : [
      {
        instance_name = srv.name
        instance_type = srv.type
        subnet_id     = srv.subnet_id
        ami_id        = srv.ami_id
        rootdisk      = srv.root_block_device
        blockdisks    = srv.ebs_block_devices
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

  root_block_device {
    volume_type = each.value.rootdisk.volume_type
    volume_size = each.value.rootdisk.volume_size
  }
}
