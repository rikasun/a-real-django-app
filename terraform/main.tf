variable "aws_region" {
  description = "The AWS region where resources will be created"
  type        = string
  default     = "us-east-1"
}
variable "s3_bucket_name" {
  description = "The name of the S3 bucket to create"
  type        = string
}
variable "instance_type" {
  description = "The type of EC2 instance to launch"
  type        = string
  default     = "t2.micro"
}
variable "key_name" {
  description = "The name of the key pair to use for SSH access"
  type        = string
}

variable "vpc_cidr" {
  description = "CIDR block for VPC"
  type        = string
  default     = "10.0.0.0/16"
}

variable "private_subnets" {
  description = "List of private subnet CIDR blocks"
  type        = list(string)
  default     = ["10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24"]
}

variable "availability_zones" {
  description = "List of availability zones"
  type        = list(string)
  default     = ["us-west-2a", "us-west-2b", "us-west-2c"]
}

variable "asg_desired_capacity" {
  description = "Desired capacity for ASG"
  type        = number
  default     = 2
}

variable "asg_max_size" {
  description = "Maximum size for ASG"
  type        = number
  default     = 4
}

variable "asg_min_size" {
  description = "Minimum size for ASG"
  type        = number
  default     = 1
}

variable "environment" {
  description = "Environment name for SOC 2 compliance"
  type        = string
  validation {
    condition     = contains(["production", "staging", "development"], var.environment)
    error_message = "Environment must be production, staging, or development."
  }
}

variable "allowed_egress_cidr" {
  description = "Allowed CIDR blocks for egress traffic"
  type        = string
  validation {
    condition     = can(cidrhost(var.allowed_egress_cidr, 0))
    error_message = "Must be a valid CIDR block."
  }
}

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