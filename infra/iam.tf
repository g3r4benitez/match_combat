# =============================================
# IAM Role for App Runner to access Secrets Manager + S3
# (Instance role - attached to the App Runner service containers)
# =============================================
resource "aws_iam_role" "apprunner_instance" {
  name = "${var.project_name}-apprunner-instance-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action    = "sts:AssumeRole"
        Effect    = "Allow"
        Principal = {
          Service = "build.apprunner.amazonaws.com"
        }
      }
    ]
  })

  tags = {
    Environment = var.environment
  }
}

resource "aws_iam_role_policy" "apprunner_instance_policy" {
  name = "${var.project_name}-apprunner-instance-policy"
  role = aws_iam_role.apprunner_instance.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = [
          "secretsmanager:GetSecretValue",
          "secretsmanager:DescribeSecret"
        ]
        Effect = "Allow"
        Resource = [
          aws_secretsmanager_secret.db_credentials.arn,
          aws_secretsmanager_secret.jwt_secret.arn
        ]
      },
      {
        Action   = ["s3:GetObject"]
        Effect   = "Allow"
        Resource = "${aws_s3_bucket.assets.arn}/*"
      }
    ]
  })
}

# =============================================
# IAM Role for App Runner to pull images from ECR
# (Access role - used during service deployment to pull container images)
# =============================================
resource "aws_iam_role" "apprunner_access" {
  name = "${var.project_name}-apprunner-access-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action    = "sts:AssumeRole"
        Effect    = "Allow"
        Principal = {
          Service = "build.apprunner.amazonaws.com"
        }
      }
    ]
  })

  tags = {
    Environment = var.environment
  }
}

resource "aws_iam_role_policy" "apprunner_access_policy" {
  name = "${var.project_name}-apprunner-access-policy"
  role = aws_iam_role.apprunner_access.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = [
          "ecr:GetAuthorizationToken",
          "ecr:BatchCheckLayerAvailability",
          "ecr:BatchGetImage",
          "ecr:GetDownloadUrlForLayer"
        ]
        Effect   = "Allow"
        Resource = "*"
      }
    ]
  })
}

# =============================================
# VPC Connector Security Group
# =============================================
resource "aws_security_group" "app_runner_vpc" {
  name        = "${var.project_name}-apprunner-vpc-sg"
  description = "Security group for App Runner VPC connector"
  vpc_id      = aws_vpc.main.id

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "${var.project_name}-apprunner-vpc-sg"
  }
}

# =============================================
# App Runner VPC Connector
# =============================================
resource "aws_apprunner_vpc_connector" "main" {
  connector_name = "${var.project_name}-vpc-connector"
  subnetworks    = [aws_subnet.private_a.id, aws_subnet.private_b.id]
  security_groups = [aws_security_group.app_runner_vpc.id]
}
