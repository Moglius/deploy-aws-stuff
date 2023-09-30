variable "configuration" {
  description = "AWS EC2 instances"
  type = list(object({
    name      = string
    type      = string
    region    = string
    ami_id    = string
    subnet_id = string
    root_block_device = object({
      volume_type = string
      volume_size = number
    })
    ebs_block_devices = list(object({
      device_name = string
      volume_size = number
      volume_type = string
    }))
    tags = any
  }))
  default = [{
    name      = "value"
    type      = "value"
    region    = "value"
    ami_id    = "value"
    subnet_id = "value"
    root_block_device = {
      volume_type = "gp3"
      volume_size = 8
    }
    ebs_block_devices = []
    tags              = {}
  }]
}
