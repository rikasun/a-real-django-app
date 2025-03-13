
variable "key_name" {
  description = "The name of the key pair to use for SSH access"
  type        = string
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