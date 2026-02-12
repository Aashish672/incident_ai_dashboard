# AWS Deployment Guide for Incident AI Dashboard

## Prerequisites
- AWS CLI configured (`aws configure`)
- Docker installed and running
- An AWS account with ECR, ECS, RDS, ElastiCache access

---

## Option 1: AWS ECS Fargate (Recommended)

### Step 1: Create Infrastructure

```bash
# Create ECR repository
aws ecr create-repository --repository-name incident-ai-dashboard

# Create RDS PostgreSQL instance
aws rds create-db-instance \
  --db-instance-identifier incident-ai-db \
  --db-instance-class db.t3.micro \
  --engine postgres \
  --master-username postgres \
  --master-user-password YOUR_DB_PASSWORD \
  --allocated-storage 20

# Create ElastiCache Redis cluster
aws elasticache create-cache-cluster \
  --cache-cluster-id incident-ai-redis \
  --cache-node-type cache.t3.micro \
  --engine redis \
  --num-cache-nodes 1
```

### Step 2: Push Docker Image to ECR

```bash
# Login to ECR
aws ecr get-login-password --region YOUR_REGION | docker login --username AWS --password-stdin YOUR_ACCOUNT_ID.dkr.ecr.YOUR_REGION.amazonaws.com

# Build and tag
docker build -t incident-ai-dashboard .
docker tag incident-ai-dashboard:latest YOUR_ACCOUNT_ID.dkr.ecr.YOUR_REGION.amazonaws.com/incident-ai-dashboard:latest

# Push
docker push YOUR_ACCOUNT_ID.dkr.ecr.YOUR_REGION.amazonaws.com/incident-ai-dashboard:latest
```

### Step 3: Store Secrets in SSM Parameter Store

```bash
aws ssm put-parameter --name "/incident-ai/SECRET_KEY" --value "YOUR_SECRET" --type "SecureString"
aws ssm put-parameter --name "/incident-ai/DB_NAME" --value "incident_ai" --type "String"
aws ssm put-parameter --name "/incident-ai/DB_USER" --value "postgres" --type "String"
aws ssm put-parameter --name "/incident-ai/DB_PASSWORD" --value "YOUR_PASSWORD" --type "SecureString"
aws ssm put-parameter --name "/incident-ai/DB_HOST" --value "YOUR_RDS_ENDPOINT" --type "String"
aws ssm put-parameter --name "/incident-ai/REDIS_URL" --value "redis://YOUR_ELASTICACHE_ENDPOINT:6379" --type "String"
aws ssm put-parameter --name "/incident-ai/EMAIL_HOST_USER" --value "your@email.com" --type "String"
aws ssm put-parameter --name "/incident-ai/EMAIL_HOST_PASSWORD" --value "YOUR_APP_PASSWORD" --type "SecureString"
```

### Step 4: Create ECS Cluster and Deploy

```bash
# Create cluster
aws ecs create-cluster --cluster-name incident-ai-cluster

# Register task definition (update placeholders in ecs-task-definition.json first)
aws ecs register-task-definition --cli-input-json file://deploy/aws/ecs-task-definition.json

# Create service
aws ecs create-service \
  --cluster incident-ai-cluster \
  --service-name incident-ai-service \
  --task-definition incident-ai-dashboard \
  --desired-count 1 \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[YOUR_SUBNET],securityGroups=[YOUR_SG],assignPublicIp=ENABLED}"
```

### Step 5: Run Migrations

```bash
aws ecs run-task \
  --cluster incident-ai-cluster \
  --task-definition incident-ai-dashboard \
  --launch-type FARGATE \
  --overrides '{"containerOverrides":[{"name":"web","command":["python","manage.py","migrate"]}]}' \
  --network-configuration "awsvpcConfiguration={subnets=[YOUR_SUBNET],securityGroups=[YOUR_SG],assignPublicIp=ENABLED}"
```

---

## Option 2: AWS EC2 with Docker Compose

### Step 1: Launch EC2 Instance

- AMI: Amazon Linux 2023
- Instance type: `t3.small` (minimum)
- Security group: Allow ports 22, 80, 443

### Step 2: Install Docker

```bash
sudo yum update -y
sudo yum install -y docker
sudo systemctl start docker
sudo usermod -aG docker ec2-user

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

### Step 3: Clone and Deploy

```bash
git clone https://github.com/Aashish672/incident-ai-dashboard.git
cd incident-ai-dashboard
git checkout feature/industry-grade

# Create .env from template
cp .env.example .env
nano .env  # Fill in your values

# Build and run
docker-compose up -d

# Run migrations
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py createsuperuser
```

---

## Environment Variables Checklist

| Variable | Required | Description |
|---|---|---|
| `SECRET_KEY` | ✅ | Django secret key (generate a new one!) |
| `DEBUG` | ✅ | `False` for production |
| `DB_NAME` | ✅ | PostgreSQL database name |
| `DB_USER` | ✅ | PostgreSQL username |
| `DB_PASSWORD` | ✅ | PostgreSQL password |
| `DB_HOST` | ✅ | RDS endpoint or `db` (docker-compose) |
| `DB_PORT` | ❌ | Default: `5432` |
| `REDIS_URL` | ✅ | ElastiCache endpoint or `redis://redis:6379/0` |
| `EMAIL_HOST_USER` | ✅ | Gmail address |
| `EMAIL_HOST_PASSWORD` | ✅ | Gmail App Password |
| `ALLOWED_HOSTS` | ✅ | Your domain/IP |
| `CSRF_TRUSTED_ORIGINS` | ✅ | `https://yourdomain.com` |
