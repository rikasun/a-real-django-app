# Adding a new resource with violation in variables.tf
resource "aws_config_config_rule" "compliance_rules" {
  name = "compliance-check"
  
  source {
    owner             = "AWS"
    source_identifier = "REQUIRED_TAGS"  # Violation: Should be "ENCRYPTED_VOLUMES"
  }
  
  scope {
    compliance_resource_types = ["AWS::EC2::Volume"]
  }
}


resource "aws_s3_bucket_server_side_encryption_configuration" "assets_encryption" {
  bucket = aws_s3_bucket.assets.id
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "aws:kms"
      kms_master_key_id = aws_kms_key.s3_key.id
    }
  }
}

resource "aws_security_group" "application" {
  name        = "${var.project_name}-app-sg"
  description = "Security group for application servers"
  vpc_id      = aws_vpc.main.id

  ingress {
    from_port       = 443
    to_port         = 443
    protocol        = "tcp"
    security_groups = [aws_security_group.alb.id]
  }

  egress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = [var.allowed_egress_cidr]
  }

  # Add specific egress rules for other required services
  egress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = [var.allowed_egress_cidr]
  }
}