# AWS Deployment Guide — Match Combat

## Overview

This document describes how to deploy the Match Combat FastAPI application to AWS using Terraform for Infrastructure as Code (IaC).

The deployment uses **AWS App Runner** as a fully-managed container service, backed by **RDS PostgreSQL** for data persistence and **S3** for static asset hosting (PDF footer sponsors image).

---

## AWS Services Used

| Service | Terraform Resource | Purpose | Cost Considerations |
|---|---|---|---|
| **App Runner** | `aws_apprunner_service` | Host the FastAPI application as a container | Pay per second of compute; starts at ~$0.064/vCPU-hr |
| **RDS PostgreSQL** | `aws_db_instance` | Managed PostgreSQL database | `db.t3.micro` (free tier eligible) |
| **S3** | `aws_s3_bucket` | Static assets (sponsors.png) + optional PDF exports | Pay per GB stored/transferred |
| **ECR** | `aws_ecr_repository` | Docker container image registry | Pay per GB stored + data transfer |
| **Secrets Manager** | `aws_secretsmanager_secret` | Store DB credentials + JWT secret | ~$0.40/secret/month + API calls |
| **VPC** | `aws_vpc`, `aws_subnet`, etc. | Isolated network for RDS (private subnets) | No additional cost |
| **CloudWatch** | `aws_cloudwatch_log_group` | Application logs | Pay per GB ingested |
| **IAM** | `aws_iam_role`, `aws_iam_policy` | App Runner permissions (ECR pull, Secrets Manager, S3) | No additional cost |
| **NAT Gateway** | `aws_nat_gateway` | Private subnet internet access for RDS updates | ~$0.045/hr + data processing |
| **VPC Connector** | `aws_apprunner_vpc_connector` | Connects App Runner to VPC (private RDS access) | ~$0.064/hr |
| **CloudFront** | *(not currently configured)* | Optional CDN for S3 assets | Pay per request/transfer |

---

## Architecture Diagram

```
                    Internet
                         |
                         v
                   App Runner
                 (public endpoint)
                         |
                         | VPC Connector (private)
                         v
              ┌─────────────────────┐
              │    VPC (10.0.0.0/16) │
              │                     │
              │  Private Subnets    │
              │  ┌───────────────┐  │
              │  │  RDS Postgres │  │
              │  │  (port 5432)  │  │
              │  └───────────────┘  │
              └─────────────────────┘
                         |
                         | IAM
                         v
              Secrets Manager + S3
```

---

## Prerequisites

1. **AWS Account** with appropriate permissions (or an IAM user with Terraform-compatible access)
2. **AWS CLI** installed and configured:
   ```bash
   aws configure
   ```
3. **Terraform** v1.0+ installed:
   ```bash
   terraform --version
   ```
4. **Docker** installed and running
5. **Python 3.11+** (for local testing)

---

## Deployment Steps

### Step 1: Configure Terraform Variables

```bash
cd infra
cp terraform.tfvars.example terraform.tfvars
```

Edit `terraform.tfvars` and set at minimum:

```hcl
jwt_secret_key = "your-very-long-random-jwt-secret-here"
admin_password = "your-secure-initial-admin-password"

# Optional (defaults shown):
# aws_region = "us-east-1"
# environment = "prod"
# db_instance_class = "db.t3.micro"
```

### Step 2: Initialize & Apply Terraform

```bash
cd infra
terraform init
terraform plan    # Review what will be created
terraform apply   # Type "yes" to confirm
```

**Expected resources created (17 total):**
- 1 VPC with 4 subnets + IGW + NAT Gateway
- 1 RDS PostgreSQL instance
- 1 S3 bucket with sponsors.png uploaded
- 2 Secrets Manager secrets (DB credentials + JWT key)
- 2 IAM roles + policies
- 1 VPC connector
- 1 ECR repository
- 1 App Runner service with auto-scaling

### Step 3: Build & Push Docker Image

```bash
cd ..
./scripts/deploy.sh
```

This script:
1. Builds the Docker image from `Dockerfile`
2. Authenticates to ECR
3. Tags and pushes the image as `:latest`
4. Triggers a new App Runner deployment

### Step 4: Verify Deployment

```bash
# Get the App Runner URL from Terraform output
cd infra
terraform output app_runner_url

# Test the health endpoint
curl https://<app-runner-url>/api/ping

# Should return: {"message":"pong"}
```

---

## Environment Variables

The App Runner service receives these environment variables:

| Variable | Source | Sensitive |
|---|---|---|
| `DB_USER` | Terraform variable | No |
| `DB_NAME` | Terraform variable | No |
| `DB_HOST` | RDS endpoint (Terraform output) | No |
| `DB_PORT` | RDS port (5432) | No |
| `DB_URL` | *(not set — constructed from components above)* | N/A |
| `NOMBRE_EVENTO` | Terraform variable | No |
| `JWT_ACCESS_TOKEN_EXPIRE_MINUTES` | Terraform variable | No |
| `JWT_REFRESH_TOKEN_EXPIRE_DAYS` | Terraform variable | No |
| `PASSWORD_RESET_EXPIRE_HOURS` | Terraform variable | No |
| `ADMIN_USERNAME` | Terraform variable | No |
| `ADMIN_PASSWORD` | Terraform variable (visible in console) | **Yes** |
| `ADMIN_EMAIL` | Terraform variable | No |
| `AWS_REGION` | Terraform variable | No |
| `S3_SPONSORS_BUCKET` | S3 bucket name (Terraform output) | No |
| `IS_DEBUG` | Terraform variable | No |

### Secrets injected via Secrets Manager (not visible in console)

| Variable | Secret Name |
|---|---|
| `DB_PASSWORD` | `match-combat/database/credentials` |
| `JWT_SECRET_KEY` | `match-combat/jwt/secret-key` |

**Note:** Currently, `DB_PASSWORD` and `JWT_SECRET_KEY` are passed as runtime environment variables (visible in App Runner console). The Terraform config also stores them in Secrets Manager. For a production setup, consider using App Runner's `secrets` feature to inject these from Secrets Manager.

---

## File Structure (Post-Deployment)

```
match_combat/
├── Dockerfile              # App container (updated: copies alembic + static)
├── infra/                  # Terraform infrastructure IaC
│   ├── versions.tf         # Provider + backend configuration
│   ├── variables.tf        # All input variables
│   ├── vpc.tf              # VPC, subnets, NAT, route tables
│   ├── rds.tf              # RDS PostgreSQL instance
│   ├── secrets.tf          # Secrets Manager + S3 bucket + sponsors upload
│   ├── iam.tf              # IAM roles for App Runner (ECR + instance)
│   ├── apprunner.tf        # App Runner service + auto-scaling
│   ├── outputs.tf          # Output values (URL, endpoints)
│   └── terraform.tfvars.example
├── scripts/
│   └── deploy.sh           # Build → ECR → App Runner deploy script
├── app/                    # FastAPI application source
│   ├── main.py             # FastAPI entry point + lifespan
│   ├── core/
│   │   ├── config.py       # (Updated) + SMTP + S3 config vars
│   │   ├── database.py     # (Updated) Alembic migrations enabled
│   │   └── logger.py       # Logging to stdout + /tmp/logs
│   ├── services/
│   │   ├── email_service.py    # (Fix) SMTP vars defined in config
│   │   ├── entrada_pdf_service.py  # (Updated) S3 sponsors loading
│   │   └── auth_service.py     # JWT auth + password reset
│   └── ...
├── alembic/                # Database migrations
│   ├── env.py              # Uses DB_URL from config
│   └── versions/
│       └── initial_schema.py
├── alembic.ini             # Alembic config
└── static/
    └── images/
        └── sponsors.png    # Uploaded to S3 via Terraform
```

---

## Post-Deployment Notes

### Database Migrations
Migrations run automatically on App Runner startup via `app/core/database.py:init_db()`. The Alembic config reads `DB_URL` from environment variables.

### Sponsors Image
- `static/images/sponsors.png` is uploaded to S3 during `terraform apply`
- The app downloads it from S3 at PDF generation time using the `S3_SPONSORS_BUCKET` env var
- If S3 is not configured, the app falls back to local filesystem

### Logs
- App Runner logs are automatically sent to CloudWatch
- The app also writes to `/tmp/logs/app.log` (ephemeral — use CloudWatch for persistence)

### Initial Admin User
On first startup, the app seeds:
- An admin user (username/email/password from env vars)
- A default Evento and Sexo records (Masculino, Femenino, Otro)

Login at `POST /api/auth/login` with OAuth2 form:
```bash
curl -X POST https://<app-runner-url>/api/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=<ADMIN_PASSWORD>"
```

---

## Common Operations

### Update Environment Variables
```bash
cd infra
terraform apply -var="jwt_access_token_expire_minutes=60"
```

### Manual Migration (if startup migration fails)
```bash
# Connect to RDS (from a bastion or local with VPN)
psql -h $(terraform output rds_endpoint) -U match_user -d match_combat

# Or run alembic manually inside a running container
docker exec -it <container> alembic upgrade head
```

### Upload New Sponsors Image
```bash
aws s3 cp static/images/sponsors.png \
  s3://match-combat-assets-prod/sponsors.png
```

### Destroy Infrastructure
```bash
cd infra
terraform destroy
```
**Note:** RDS will take a final snapshot (configurable via `skip_final_snapshot`).

---

## Troubleshooting

| Issue | Cause | Fix |
|---|---|---|
| App Runner can't connect to RDS | VPC connector misconfiguration | Check `aws_apprunner_vpc_connector` subnets match RDS subnet group |
| Migrations fail on startup | Alembic.ini not in container | Ensure Dockerfile copies `alembic/` and `alembic.ini` |
| PDF generation fails | sponsors.png not in S3 | Run `terraform apply` to upload the image |
| Login fails | Wrong admin password | Check `terraform.tfvars` `admin_password` |
| CORS errors from frontend | Wildcard CORS enabled | Configure specific allowed origins in `main.py` |

---

## Cost Optimization Tips

1. **RDS**: Use `db.t3.micro` (free tier eligible for 750 hrs/month for 12 months)
2. **App Runner**: Start with `Standard1` (1 vCPU, 2GB RAM). Scale to `Standard2` or higher if needed
3. **App Runner auto-scaling**: Min 1 instance, max 3 (adjust in `apprunner.tf`)
4. **Delete when not in use**: `terraform destroy` to tear down all resources
5. **ECR lifecycle**: Keeps last 30 images automatically
