provider "aws" {
  region = var.aws_region
}

# VPC Configuration
module "vpc" {
  source = "./modules/vpc"
  
  environment     = var.environment
  vpc_cidr        = var.vpc_cidr
  azs             = var.availability_zones
  private_subnets = var.private_subnet_cidrs
  public_subnets  = var.public_subnet_cidrs
}

# ECS Cluster
module "ecs" {
  source = "./modules/ecs"
  
  environment    = var.environment
  vpc_id         = module.vpc.vpc_id
  subnet_ids     = module.vpc.private_subnet_ids
  app_image      = var.app_image
  container_port = var.container_port
  depends_on     = [module.vpc]
}

# RDS Instance
module "rds" {
  source = "./modules/rds"
  
  environment    = var.environment
  vpc_id         = module.vpc.vpc_id
  subnet_ids     = module.vpc.private_subnet_ids
  instance_class = var.db_instance_class
  db_name        = var.db_name
  db_username    = var.db_username
  db_password    = var.db_password
}

resource "aws_security_group" "web_server" {
  name        = "web_server"
  description = "Allow web traffic"

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_cloudtrail" "main_trail" {
  name                          = "main-trail"
  s3_bucket_name                = aws_s3_bucket.my_react_app_bucket.bucket
  is_multi_region_trail         = false
  enable_log_file_validation    = false
  include_global_service_events = true
}

# Redis Cache
module "redis" {
  source = "./modules/redis"
  
  environment    = var.environment
  vpc_id         = module.vpc.vpc_id
  subnet_ids     = module.vpc.private_subnet_ids
  instance_type  = var.redis_instance_type
}

# Application Load Balancer
module "alb" {
  source = "./modules/alb"
  
  environment    = var.environment
  vpc_id         = module.vpc.vpc_id
  subnet_ids     = module.vpc.public_subnet_ids
  ecs_service_id = module.ecs.service_id
} 