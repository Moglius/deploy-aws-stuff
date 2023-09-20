locals {
  ebs_volumes = flatten([
    for ebs in var.ebs_volumes : [
      {
        instance_name = ebs.instance_name
        volume_type   = ebs.volume_type
        volume_size   = ebs.volume_size
        device_name   = ebs.device_name
        instance_id   = ebs.instance_id
        instance_az   = ebs.instance_az
      }
    ]
  ])
}

resource "aws_ebs_volume" "ebs_volumes" {
  for_each          = { for ebs_volume in local.ebs_volumes : "${ebs_volume.instance_id}-${ebs_volume.device_name}" => ebs_volume }
  availability_zone = each.value.instance_az
  size              = each.value.volume_size
  type              = each.value.volume_type
  tags = {
    InstanceID   = each.value.instance_id
    InstanceName = each.value.instance_name
  }
}
