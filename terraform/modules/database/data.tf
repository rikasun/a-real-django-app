# Get current AWS region
data "aws_region" "current" {}

# Get current AWS account ID
data "aws_caller_identity" "current" {}

# Get information about existing KMS keys (optional)
data "aws_kms_alias" "rds" {
  name = "alias/aws/rds"
}

locals {
  # Environment specific settings
  is_production = var.environment == "production"
  
  # RDS settings
  rds_config = {
    storage = {
      encrypted = true
      min_size  = 100
      max_size  = 500
    }
    backup = {
      retention_period = local.is_production ? 30 : 7
      window          = "03:00-04:00"
    }
    monitoring = {
      interval                = 60
      retention_period        = local.is_production ? 7 : 5
      log_types              = ["postgresql", "upgrade"]
    }
    maintenance = {
      window = "Mon:04:00-Mon:05:00"
    }
  }

  # Common tags
  common_tags = {
    Environment     = var.environment
    Managed_by     = "terraform"
    Owner          = "data-team"
    Cost_center    = "analytics-${var.environment}"
  }

  # Security settings
  security = {
    deletion_protection = local.is_production
    multi_az           = local.is_production
    instance_class     = local.is_production ? "db.t3.large" : "db.t3.medium"
  }
} 