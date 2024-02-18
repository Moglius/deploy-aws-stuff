
module "vpc" {
  source = "terraform-aws-modules/vpc/aws"

  name = "my-vpc"
  cidr = "10.0.0.0/16"

  azs             = ["us-east-2a", "us-east-2b"]
  private_subnets = ["10.0.1.0/24", "10.0.2.0/24"]
  public_subnets  = ["10.0.101.0/24", "10.0.102.0/24"]

  tags = {
    Terraform   = "true"
    Environment = "dev"
  }
}

resource "aws_lb_trust_store" "truststore" {
  name = "trust-store-alb"

  ca_certificates_bundle_s3_bucket = "terraform-state-12321456"
  ca_certificates_bundle_s3_key    = "truststore.pem"

}

module "alb" {
  source = "terraform-aws-modules/alb/aws"

  name    = "my-alb"
  vpc_id  = module.vpc.vpc_id
  subnets = module.vpc.public_subnets

  enable_deletion_protection = false

  security_groups = [aws_security_group.allow_all.id]

  access_logs = {
    bucket = module.log_bucket.s3_bucket_id
    prefix = "access-logs"
  }

  listeners = {
    ex-http-https-redirect = {
      port     = 80
      protocol = "HTTP"
      redirect = {
        port        = "443"
        protocol    = "HTTPS"
        status_code = "HTTP_301"
      }
    }
    ex-https = {
      port            = 443
      protocol        = "HTTPS"
      certificate_arn = "arn:aws:acm:us-east-2:456639116688:certificate/860cf895-4831-4383-9050-2b287c7b237a"

      mutual_authentication = {
        mode            = "verify"
        trust_store_arn = aws_lb_trust_store.truststore.arn
      }

      forward = {
        target_group_key = "web-instance"
      }
    }
  }

  target_groups = {
    web-instance = {
      target_id   = aws_instance.server.id
      protocol    = "HTTP"
      port        = 80
      target_type = "instance"
    }
  }

  tags = {
    Environment = "Development"
    Project     = "Example"
  }

  depends_on = [aws_instance.server]
}

resource "aws_instance" "server" {

  ami                         = "ami-0c20d88b0021158c6"
  instance_type               = "t2.micro"
  subnet_id                   = module.vpc.public_subnets[0]
  security_groups             = [aws_security_group.allow_all.id]
  associate_public_ip_address = true

  user_data = <<-EOF
    #!/bin/bash
    echo "Change user password"
    echo 'ec2-user:Qwerty123' | chpasswd
    yum install -y nginx
    systemctl restart nginx
    EOF

  tags = {
    Name        = "web_server"
    Terraform   = "true"
    Environment = "dev"
  }
}

module "log_bucket" {
  source  = "terraform-aws-modules/s3-bucket/aws"
  version = "~> 3.0"

  bucket_prefix = "my-alb-logs-"
  acl           = "log-delivery-write"

  # For example only
  force_destroy = true

  control_object_ownership = true
  object_ownership         = "ObjectWriter"

  attach_elb_log_delivery_policy = true # Required for ALB logs
  attach_lb_log_delivery_policy  = true # Required for ALB/NLB logs

  attach_deny_insecure_transport_policy = true
  attach_require_latest_tls_policy      = true

}
