# =============================================
# ECR (Elastic Container Registry)
# =============================================
resource "aws_ecr_repository" "app" {
  name                 = "${var.project_name}/api"
  image_tag_mutability = "MUTABLE"
  force_delete         = true

  image_scanning_configuration {
    scan_on_push = true
  }

  lifecycle_policy {
    policy = jsonencode({
      rules = [
        {
          rulePriority = 1
          description  = "Keep last 30 images"
          selection = {
            tagged      = false
            countType   = "imageCountBased"
            countNumber = 30
          }
          action = {
            type = "expire"
          }
        }
      ]
    })
  }

  tags = {
    Name        = "${var.project_name}-ecr"
    Environment = var.environment
  }
}

# =============================================
# CloudWatch Log Group
# =============================================
resource "aws_cloudwatch_log_group" "apprunner_logs" {
  name              = "/aws/apprunner/${var.project_name}"
  retention_in_days = 30
  tags = {
    Environment = var.environment
  }
}

# =============================================
# Auto Scaling Configuration
# =============================================
resource "aws_apprunner_auto_scaling_configuration_version" "app" {
  resource_name = "${var.project_name}-autoscaling"

  autoscaling_parameters {
    max_concurrency = 50
    min_instances   = 1
    max_instances   = 5
  }

  tags = {
    Environment = var.environment
  }
}

# =============================================
# App Runner Service
# =============================================
resource "aws_apprunner_service" "api" {
  service_name = "${var.project_name}-service"

  source_configuration {
    authentication_configuration {
      access_role_arn = aws_iam_role.apprunner_access.arn
    }

    image_repository {
      image_identifier = "${aws_ecr_repository.app.repository_url}:latest"
      image_configuration {
        port = tostring(var.app_port)
        runtime_environment_variables = {
          IS_DEBUG                          = tostring(var.is_debug)
          DB_USER                           = var.db_username
          DB_NAME                           = var.db_name
          DB_HOST                           = aws_db_instance.postgres.address
          DB_PORT                           = tostring(aws_db_instance.postgres.port)
          NOMBRE_EVENTO                     = var.nombre_evento
          JWT_ACCESS_TOKEN_EXPIRE_MINUTES     = tostring(var.jwt_access_token_expire_minutes)
          JWT_REFRESH_TOKEN_EXPIRE_DAYS       = tostring(var.jwt_refresh_token_expire_days)
          PASSWORD_RESET_EXPIRE_HOURS         = tostring(var.password_reset_expire_hours)
          ADMIN_USERNAME                      = var.admin_username
          ADMIN_PASSWORD                      = var.admin_password
          ADMIN_EMAIL                         = var.admin_email
          AWS_REGION                          = var.aws_region
          S3_SPONSORS_BUCKET                  = aws_s3_bucket.assets.bucket
        }
      }
    }

    auto_deployments_enabled = false
  }

  instance_configuration {
    instance_class    = "Standard1"
    instance_role_arn = aws_iam_role.apprunner_instance.arn
  }

  network_configuration {
    egress_type = "VPC"
    egress_configuration {
      vpc_connector_arn = aws_apprunner_vpc_connector.main.arn
      egress_vpc_only   = true
    }
  }

  observability_configuration {
    observability_enabled = true
    visibility            = "VISIBLE"
  }

  health_check_configuration {
    protocol            = "TCP"
    port                = tostring(var.app_port)
    healthy_threshold     = 2
    unhealthy_threshold   = 5
    timeout               = "10s"
    interval              = "30s"
  }

  auto_scaling_configuration_version = aws_apprunner_auto_scaling_configuration_version.app.version

  tags = {
    Environment = var.environment
    Name        = "${var.project_name}-apprunner"
  }

  depends_on = [aws_ecr_repository.app]
}
