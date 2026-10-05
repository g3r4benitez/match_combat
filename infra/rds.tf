# =============================================
# Random password for DB
# =============================================
resource "random_password" "db_password" {
  length  = 32
  special = true
}

# =============================================
# DB Subnet Group
# =============================================
resource "aws_db_subnet_group" "main" {
  name       = "${var.project_name}-db-subnet-group"
  subnet_ids = [aws_subnet.private_a.id, aws_subnet.private_b.id]
  tags = {
    Name = "${var.project_name}-db-subnet-group"
  }
}

# =============================================
# RDS Security Group
# =============================================
resource "aws_security_group" "rds" {
  name        = "${var.project_name}-rds-sg"
  description = "Allow PostgreSQL from App Runner"
  vpc_id      = aws_vpc.main.id

  ingress {
    from_port         = 5432
    to_port           = 5432
    protocol          = "tcp"
    security_groups   = [aws_security_group.app_runner_vpc.id]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "${var.project_name}-rds-sg"
  }
}

# =============================================
# RDS PostgreSQL Instance
# =============================================
resource "aws_db_instance" "postgres" {
  identifier                  = "${var.project_name}-db"
  engine                      = "postgres"
  engine_version              = "16"
  instance_class              = var.db_instance_class
  allocated_storage           = 20
  max_allocated_storage       = 100
  db_name                     = var.db_name
  username                    = var.db_username
  password                    = random_password.db_password.result
  db_subnet_group_name        = aws_db_subnet_group.main.name
  vpc_security_group_ids      = [aws_security_group.rds.id]
  publicly_accessible         = false
  skip_final_snapshot         = false
  final_snapshot_identifier   = "${var.project_name}-final-snapshot"
  backup_retention_period     = 7
  backup_window               = "03:00-04:00"
  maintenance_window          = "sun:05:00-sun:06:00"
  deletion_protection         = var.environment == "prod"
  storage_type                = "gp3"
  apply_immediately           = var.environment == "dev"

  tags = {
    Name        = "${var.project_name}-rds"
    Environment = var.environment
  }
}
