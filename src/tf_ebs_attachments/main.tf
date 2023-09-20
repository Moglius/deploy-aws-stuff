locals {
  ebs_attachments = flatten([
    for ebs_attachment in var.ebs_attachments : [
      {
        volume_id     = ebs_attachment.volume_id
        device_name   = ebs_attachment.device_name
        instance_id   = ebs_attachment.instance_id
        instance_name = ebs_attachment.instance_name
      }
    ]
  ])
}

resource "aws_volume_attachment" "ebs_attachments" {
  for_each = { for ebs_attachment in local.ebs_attachments : "${ebs_attachment.instance_id}-${ebs_attachment.volume_name}" => ebs_attachment }

  device_name = each.value.device_name
  volume_id   = each.value.volume_id
  instance_id = each.value.instance_id
}
