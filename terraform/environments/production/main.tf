module "networking" {
  source = "../../modules/networking"

  environment     = var.environment
  vpc_cidr        = "10.0.0.0/16"
  azs             = ["us-west-2a", "us-west-2b", "us-west-2c"]
  private_subnets = ["10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24"]
  public_subnets  = ["10.0.101.0/24", "10.0.102.0/24", "10.0.103.0/24"]
}

module "database" {
  source = "../../modules/database"

  environment      = var.environment
  instance_type    = var.instance_type
  multi_az         = var.multi_az
  storage_size     = 100
  backup_retention = 30
  vpc_id           = module.networking.vpc_id
  subnet_ids       = module.networking.private_subnet_ids
}

module "cache" {
  source = "../../modules/cache"

  environment   = var.environment
  cluster_size  = 2
  instance_type = "cache.t3.medium"
  vpc_id        = module.networking.vpc_id
  subnet_ids    = module.networking.private_subnet_ids
}

module "monitoring" {
  source = "../../modules/monitoring"

  environment     = var.environment
  alarm_sns_topic = aws_sns_topic.alerts.arn
  dashboard_name  = "${var.project_name}-${var.environment}"
} 