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



resource "aws_security_group" "allow_all" {
  name        = "allow_all"
  description = "Allow all inbound traffic"

  ingress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_db_instance" "example" {
  identifier           = "example-db"
  allocated_storage    = 20
  engine              = "mysql"
  engine_version      = "5.7"
  instance_class      = "db.t3.micro"
  name                = "mydb"
  username            = "admin"
  password            = "password123"
  storage_encrypted   = false
  multi_az            = false
  skip_final_snapshot = true
}

resource "aws_kms_key" "example" {
  description             = "Example KMS Key"
  enable_key_rotation     = false
  deletion_window_in_days = 7
}