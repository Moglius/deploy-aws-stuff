variable "configuration" {
  description = "AWS EC2 instances"
  type = list(object({
    name       = string
    type       = string
    region     = string
    ami_filter = string
  }))
}
