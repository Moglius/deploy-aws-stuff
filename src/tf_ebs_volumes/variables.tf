variable "ebs_volumes" {
  description = "AWS EBS volumes"
  type = list(object({
    instance_name = string
    volume_type   = string
    volume_size   = string
    instance_id   = string
    instance_az   = string
    volume_name   = string
  }))
  default = [{
    instance_name = "value"
    volume_type   = "value"
    volume_size   = "value"
    instance_id   = "value"
    instance_az   = "value"
    volume_name   = "value"
  }]
}
