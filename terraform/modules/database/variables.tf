variable "environment" {
  description = "Environment name (e.g., prod, staging)"
  type        = string
  validation {
    condition     = contains(["development", "staging", "production"], var.environment)
    error_message = "Environment must be one of: development, staging, production"
  }
}

variable "vpc_id" {
  description = "VPC ID where the RDS instance will be created"
  type        = string
}

variable "subnet_ids" {
  description = "List of subnet IDs for the RDS subnet group"
  type        = list(string)
}

variable "allowed_cidr_blocks" {
  description = "List of CIDR blocks allowed to access the database"
  type        = list(string)
}

variable "kms_key_id" {
  description = "Optional custom KMS key ID for RDS encryption"
  type        = string
  default     = null
}

variable "custom_parameter_group_family" {
  description = "Optional custom parameter group family"
  type        = string
  default     = "postgres14"
}

variable "custom_backup_retention" {
  description = "Optional override for backup retention period"
  type        = number
  default     = null
} 