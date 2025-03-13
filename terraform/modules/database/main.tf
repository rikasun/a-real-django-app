module "security" {
  source = "../security"

  environment = var.environment
  vpc_id     = var.vpc_id
  service    = "database"
}

# KMS key for encryption
resource "aws_kms_key" "database" {
  description             = "KMS key for database encryption"
  deletion_window_in_days = 7
  enable_key_rotation     = true

  tags = {
    Environment = var.environment
    Purpose     = "database-encryption"
  }
}

resource "aws_db_instance" "main" {
  identifier        = "${var.environment}-db"
  engine           = "postgres"
  engine_version   = "13.7"
  instance_class   = var.instance_type
  allocated_storage = var.storage_size

  # SOC2 Required: Data Protection
  backup_retention_period = coalesce(var.backup_retention, 30)
  backup_window          = "03:00-04:00"
  maintenance_window     = "Mon:04:00-Mon:05:00"
  storage_encrypted      = true
  kms_key_id            = aws_kms_key.database.arn
  deletion_protection    = true
  skip_final_snapshot    = false
  final_snapshot_identifier = "${var.environment}-db-final-snapshot"

  # SOC2 Required: Access Control
  publicly_accessible    = false
  multi_az              = true
  ca_cert_identifier    = "rds-ca-2019"

  # SOC2 Required: Monitoring
  monitoring_interval    = 1
  monitoring_role_arn   = aws_iam_role.rds_monitoring.arn
  performance_insights_enabled = true
  performance_insights_retention_period = 7
  enabled_cloudwatch_logs_exports = ["postgresql", "upgrade"]

  # SOC2 Required: Network Security
  vpc_security_group_ids = [module.security.security_group_id]
  db_subnet_group_name   = aws_db_subnet_group.main.name

  # SOC2 Required: Parameter Group Settings
  parameter_group_name = aws_db_parameter_group.main.name

  tags = {
    Name           = "${var.environment}-db"
    Environment    = var.environment
    Terraform      = "true"
    Compliance     = "soc2"
    DataSensitivity = "high"
  }
}

# SOC2 Required: Enhanced Monitoring Role
resource "aws_iam_role" "rds_monitoring" {
  name = "${var.environment}-rds-monitoring"

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
}

# SOC2 Required: Database Parameters
resource "aws_db_parameter_group" "main" {
  family = "postgres13"
  name   = "${var.environment}-db-params"

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

  parameter {
    name  = "ssl"
    value = "1"
  }
}

# SOC2 Required: Monitoring Alarms
resource "aws_cloudwatch_metric_alarm" "database_cpu" {
  alarm_name          = "${var.environment}-db-cpu-utilization"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name        = "CPUUtilization"
  namespace          = "AWS/RDS"
  period             = "300"
  statistic          = "Average"
  threshold          = "80"
  alarm_description  = "Database CPU utilization is too high"
  alarm_actions      = [var.alarm_sns_topic]

  dimensions = {
    DBInstanceIdentifier = aws_db_instance.main.id
  }
} 