resource "aws_elasticache_cluster" "redis" {
  cluster_id           = "redis-cluster"
  engine               = "redis"
  node_type            = "cache.t2.micro"
  num_cache_nodes      = 1
  parameter_group_name = "default.redis5.0"
  engine_version       = "5.0.6"
  port                 = 6379

  # Violation: Missing encryption settings
  # This violates elasticache_security.at_rest_encryption and elasticache_security.transit_encryption
  # at_rest_encryption_enabled = true
  # transit_encryption_enabled = true
} 