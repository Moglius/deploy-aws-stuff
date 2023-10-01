locals {
  srvs = flatten([
    for srv in var.configuration : [
      {
        name = srv.name
      }
    ]
  ])
}

resource "aws_servicecatalog_provisioned_product" "server" {
  for_each = { for server in local.srvs : server.name => server }

  name                     = each.value.name
  product_id               = "prod-hjtm452n6la6y"
  provisioning_artifact_id = "pa-c6jxx2damwcyg"

  provisioning_parameters {
    key   = "KeyName"
    value = "new"
  }

  tags = {
    foo  = "bar"
    Name = each.value.name
  }
}
