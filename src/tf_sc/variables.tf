variable "configuration" {
  description = "AWS srvs"
  type = list(object({
    name = string
  }))
}
