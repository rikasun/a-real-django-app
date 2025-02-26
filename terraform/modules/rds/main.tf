# Non-compliant RDS configuration (missing encryption, backups, and monitoring)
resource "aws_db_instance" "main" {
  identifier        = "${var.environment}-db"
  engine           = "postgres"
  engine_version   = "13.7"
  instance_class   = var.instance_class
  allocated_storage = 20

  # Non-compliant: Credentials in plain text
  name     = var.db_name
  username = "admin"  # Hardcoded credentials
  password = "insecure123!"  # Hardcoded password

  # Non-compliant: Public access enabled
  publicly_accessible = true

  # Non-compliant: No encryption
  storage_encrypted = false

  # Non-compliant: Minimal backup settings
  backup_retention_period = 0
  skip_final_snapshot    = true

  # Non-compliant: No monitoring
  monitoring_interval = 0
  
  # Non-compliant: Weak security group
  vpc_security_group_ids = [aws_security_group.db.id]

  tags = {
    Name        = "${var.environment}-db"
    Environment = var.environment
  }
}

# Non-compliant: Overly permissive security group
resource "aws_security_group" "db" {
  name        = "${var.environment}-db-sg"
  description = "Database security group"
  vpc_id      = var.vpc_id

  # Non-compliant: Allow all inbound traffic
  ingress {
    from_port   = 5432
    to_port     = 5432
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