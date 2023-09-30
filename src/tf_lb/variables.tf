variable "configuration" {
  description = "AWS ALBs"
  type = list(object({
    name            = string
    vpc_id          = string
    subnets         = list(string)
    security_groups = list(string)
    internal        = bool
    http_tcp_listeners = list(object({
      port               = number
      protocol           = string
      target_group_index = number
    }))
    target_groups = list(object({
      name_prefix      = string
      backend_protocol = string
      backend_port     = number
      health_check = object({
        interval            = number
        path                = string
        port                = string
        healthy_threshold   = number
        unhealthy_threshold = number
        timeout             = number
        protocol            = string
        matcher             = string
      })
      targets = map(object({
        target_id = string
        port      = number
      }))
    }))
  }))
}
