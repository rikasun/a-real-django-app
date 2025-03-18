# KMS key for RDS encryption
resource "aws_kms_key" "rds_encryption" {
  description             = "KMS key for RDS database encryption"
  deletion_window_in_days = 7
  enable_key_rotation     = true

  tags = {
    Environment = var.environment
    Purpose     = "rds-encryption"
    Managed_by  = "terraform"
  }
}

# RDS subnet group
resource "aws_db_subnet_group" "analytics" {
  name        = "analytics-${var.environment}"
  description = "Subnet group for Analytics database"
  subnet_ids  = var.subnet_ids

  tags = {
    Environment = var.environment
    Managed_by  = "terraform"
  }
}

# Security group for RDS
resource "aws_security_group" "analytics_db" {
  name        = "analytics-db-${var.environment}"
  description = "Security group for Analytics database"
  vpc_id      = var.vpc_id

  # Allow inbound PostgreSQL traffic from specified CIDR blocks
  ingress {
    from_port   = 5432
    to_port     = 5432
    protocol    = "tcp"
    cidr_blocks = var.allowed_cidr_blocks
    description = "PostgreSQL access from allowed networks"
  }

  # Controlled outbound traffic
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = var.allowed_cidr_blocks
    description = "Outbound access to allowed networks"
  }

  tags = {
    Environment = var.environment
    Managed_by  = "terraform"
    Purpose     = "database-security"
  }
}

# Parameter group for enhanced security
resource "aws_db_parameter_group" "analytics" {
  family = "postgres14"
  name   = "analytics-${var.environment}"

  parameter {
    name  = "rds.force_ssl"
    value = "1"
  }

  parameter {
    name  = "log_connections"
    value = "1"
  }

  parameter {
    name  = "log_disconnections"
    value = "1"
  }

  parameter {
    name  = "log_statement"
    value = "all"
  }

  tags = {
    Environment = var.environment
    Managed_by  = "terraform"
  }
}

# RDS instance
resource "aws_db_instance" "analytics" {
  identifier        = "analytics-${var.environment}"
  engine            = "postgres"
  engine_version    = "14.7"
  instance_class    = local.security.instance_class
  allocated_storage = local.rds_config.storage.min_size
  max_allocated_storage = local.rds_config.storage.max_size

  # Security
  storage_encrypted        = local.rds_config.storage.encrypted
  kms_key_id              = coalesce(var.kms_key_id, data.aws_kms_alias.rds.target_key_id)
  publicly_accessible     = false
  multi_az               = local.security.multi_az
  db_subnet_group_name   = aws_db_subnet_group.analytics.name
  vpc_security_group_ids = [aws_security_group.analytics_db.id]
  parameter_group_name   = aws_db_parameter_group.analytics.name

  # Monitoring
  monitoring_interval = local.rds_config.monitoring.interval
  monitoring_role_arn = aws_iam_role.rds_monitoring.arn
  enabled_cloudwatch_logs_exports = local.rds_config.monitoring.log_types
  performance_insights_enabled    = true
  performance_insights_retention_period = local.rds_config.monitoring.retention_period

  # Backup and maintenance
  backup_retention_period = local.rds_config.backup.retention_period
  backup_window          = local.rds_config.backup.window
  maintenance_window     = local.rds_config.maintenance.window
  deletion_protection    = local.security.deletion_protection
  skip_final_snapshot    = false
  final_snapshot_identifier = "analytics-${var.environment}-final-snapshot"

  tags = merge(
    local.common_tags,
    {
      Backup_enabled = "true"
      Encryption     = "true"
      Monitoring     = "enhanced"
    }
  )
}

# IAM role for enhanced monitoring
resource "aws_iam_role" "rds_monitoring" {
  name = "rds-monitoring-${var.environment}"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "monitoring.rds.amazonaws.com"
        }
      }
    ]
  })

  tags = {
    Environment = var.environment
    Purpose     = "rds-monitoring"
    Managed_by  = "terraform"
  }
}

# Attach the enhanced monitoring policy
resource "aws_iam_role_policy_attachment" "rds_monitoring" {
  role       = aws_iam_role.rds_monitoring.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonRDSEnhancedMonitoringRole"
} 