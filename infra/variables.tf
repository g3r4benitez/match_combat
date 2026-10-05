variable "aws_region" {
  description = "AWS region to deploy resources"
  type        = string
  default     = "us-east-1"
}

variable "project_name" {
  description = "Name prefix for all resources"
  type        = string
  default     = "match-combat"
}

variable "environment" {
  description = "Deployment environment (dev, staging, prod)"
  type        = string
  default     = "prod"
}

variable "db_username" {
  description = "PostgreSQL username"
  type        = string
  default     = "match_user"
}

variable "db_name" {
  description = "PostgreSQL database name"
  type        = string
  default     = "match_combat"
}

variable "db_instance_class" {
  description = "RDS instance class"
  type        = string
  default     = "db.t3.micro"
}

variable "jwt_secret_key" {
  description = "JWT signing secret (will be stored in Secrets Manager)"
  type        = string
  sensitive   = true
}

variable "nombre_evento" {
  description = "Event name displayed on PDF tickets"
  type        = string
  default     = "Match Combat"
}

variable "is_debug" {
  description = "Enable FastAPI debug mode"
  type        = bool
  default     = false
}

variable "app_port" {
  description = "Port the FastAPI app listens on"
  type        = number
  default     = 9009
}

variable "jwt_access_token_expire_minutes" {
  description = "Access token expiry in minutes"
  type        = number
  default     = 30
}

variable "jwt_refresh_token_expire_days" {
  description = "Refresh token expiry in days"
  type        = number
  default     = 7
}

variable "password_reset_expire_hours" {
  description = "Password reset token expiry in hours"
  type        = number
  default     = 1
}

variable "admin_username" {
  description = "Initial admin username"
  type        = string
  default     = "admin"
}

variable "admin_password" {
  description = "Initial admin password"
  type        = string
  sensitive   = true
}

variable "admin_email" {
  description = "Initial admin email"
  type        = string
  default     = "admin@matchcombat.local"
}
