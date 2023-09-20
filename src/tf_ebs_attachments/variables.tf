variable "ebs_attachments" {
  description = "AWS EBS volume attachments"
  type = list(object({
    instance_name = string
    instance_id   = string
    volume_id     = string
    volume_name   = string
  }))
  default = [{
    instance_name = "value"
    instance_id   = "value"
    volume_id     = "value"
    volume_name   = "value"
  }]
}
