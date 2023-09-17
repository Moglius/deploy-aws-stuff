variable "configuration" {
  description = "AWS EC2 instances"
  type = list(object({
    name   = string
    type   = string
    region = string
    ami_id = string
  }))
  default = [{
    id     = "value"
    name   = "value"
    type   = "value"
    region = "value"
    ami_id = "value"
  }]
}
