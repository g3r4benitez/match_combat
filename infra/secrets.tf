# =============================================
# S3 Bucket for static assets (sponsors image, PDF exports)
# =============================================
resource "aws_s3_bucket" "assets" {
  bucket = "${var.project_name}-assets-${var.environment}"
  acl    = "private"

  tags = {
    Name        = "${var.project_name}-assets"
    Environment = var.environment
  }
}

resource "aws_s3_bucket_public_access_block" "assets" {
  bucket = aws_s3_bucket.assets.id

  block_public_acls       = true
  block_public_policy     = true
  restrict_public_buckets = true
  ignore_public_acls      = true
}

resource "aws_s3_bucket_cors_configuration" "assets" {
  bucket = aws_s3_bucket.assets.id

  cors_rule {
    allowed_methods = ["GET"]
    allowed_origins = ["*"]
    allowed_headers = ["*"]
    max_age_seconds = 3000
  }
}

# Upload sponsors.png to S3 (from local static/images/sponsors.png)
resource "aws_s3_object" "sponsors_image" {
  bucket       = aws_s3_bucket.assets.id
  key          = "sponsors.png"
  source       = "${path.module}/../static/images/sponsors.png"
  etag         = filemd5("${path.module}/../static/images/sponsors.png")
  content_type = "image/png"
}

# =============================================
# Secrets Manager
# =============================================
# DB Connection secret (containing username, password, host, port, dbname)
resource "aws_secretsmanager_secret" "db_credentials" {
  name                    = "${var.project_name}/database/credentials"
  description             = "PostgreSQL credentials for Match Combat"
  recovery_window_in_days = 7
  tags = {
    Environment = var.environment
  }
}

resource "aws_secretsmanager_secret_version" "db_credentials" {
  secret_id = aws_secretsmanager_secret.db_credentials.id
  secret_string = jsonencode({
    username = var.db_username
    password = random_password.db_password.result
    engine   = "postgresql"
    host     = aws_db_instance.postgres.address
    port     = aws_db_instance.postgres.port
    dbname   = var.db_name
  })
}

# JWT Secret
resource "aws_secretsmanager_secret" "jwt_secret" {
  name                    = "${var.project_name}/jwt/secret-key"
  description             = "JWT signing secret for Match Combat"
  recovery_window_in_days = 7
  tags = {
    Environment = var.environment
  }
}

resource "aws_secretsmanager_secret_version" "jwt_secret" {
  secret_id     = aws_secretsmanager_secret.jwt_secret.id
  secret_string = var.jwt_secret_key
}
