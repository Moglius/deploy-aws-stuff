locals {
  albs = flatten([
    for alb in var.configuration : [
      {
        name               = alb.name
        vpc_id             = alb.vpc_id
        subnets            = alb.subnets
        security_groups    = alb.security_groups
        internal           = alb.internal
        target_groups      = alb.target_groups
        http_tcp_listeners = alb.http_tcp_listeners
      }
    ]
  ])
}

module "alb" {
  source  = "terraform-aws-modules/alb/aws"
  version = "~> 8.0"

  for_each = { for alb in local.albs : alb.name => alb }

  name               = each.value.name
  load_balancer_type = "application"

  vpc_id          = each.value.vpc_id
  subnets         = each.value.subnets
  security_groups = each.value.security_groups
  internal        = each.value.internal

  target_groups = each.value.target_groups

  http_tcp_listeners = each.value.http_tcp_listeners

  https_listeners = []

  tags = {
    Owner       = "user"
    Environment = "dev"
  }
}
