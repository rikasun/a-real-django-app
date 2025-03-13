# Root main.tf - Organize by environment
module "production" {
  source = "./environments/production"
  count  = terraform.workspace == "production" ? 1 : 0

  project_name    = var.project_name
  aws_region     = var.aws_region
  environment    = "production"
  instance_type  = "t3.medium"
  multi_az       = true
}

module "staging" {
  source = "./environments/staging"
  count  = terraform.workspace == "staging" ? 1 : 0

  project_name    = var.project_name
  aws_region     = var.aws_region
  environment    = "staging"
  instance_type  = "t3.small"
  multi_az       = false
}

# Application Load Balancer
resource "aws_lb" "app" {
  name               = "${var.project_name}-alb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.alb.id]
  subnets            = aws_subnet.public[*].id

  enable_deletion_protection = true
}