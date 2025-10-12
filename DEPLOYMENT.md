# Deployment Guide

This guide covers deploying the AI Analytics Platform to production environments.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Environment Configuration](#environment-configuration)
- [Deployment Options](#deployment-options)
- [Docker Deployment](#docker-deployment)
- [Kubernetes Deployment](#kubernetes-deployment)
- [Cloud Platform Deployments](#cloud-platform-deployments)
- [Post-Deployment](#post-deployment)
- [Monitoring and Maintenance](#monitoring-and-maintenance)

## Prerequisites

- Docker and Docker Compose (for containerized deployment)
- Kubernetes cluster (for K8s deployment)
- PostgreSQL database (managed service recommended)
- Redis cache (managed service recommended)
- Domain name and SSL certificate
- CI/CD pipeline (GitHub Actions, GitLab CI, etc.)

## Environment Configuration

### Production Environment Variables

Create a secure `.env` file with production values:

```bash
# Application
APP_NAME=AI-Analytics Platform
DEBUG=False
HOST=0.0.0.0
PORT=8000
WORKERS=4
LOG_LEVEL=INFO

# Database (use managed service)
DATABASE_URL=postgresql+asyncpg://user:password@db-host:5432/analytics
DB_POOL_SIZE=20

# Cache (use managed service)
REDIS_URL=redis://redis-host:6379

# Security (use strong random values)
SECRET_KEY=<generated-with-openssl-rand-hex-32>
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=30

# AI/ML
OPENAI_API_KEY=<your-production-api-key>
OPENAI_MODEL=gpt-4o-mini
MAX_TOKENS=2048
TEMPERATURE=0.2

# ETL
MAX_WORKERS=8
BATCH_SIZE=1000
CHUNK_SIZE=10000

# CORS (specify exact origins)
ALLOWED_ORIGINS=https://yourdomain.com,https://app.yourdomain.com
```

### Secrets Management

**Recommended approaches:**

1. **AWS Secrets Manager:**
   ```bash
   aws secretsmanager create-secret \
     --name analytics-platform-secret-key \
     --secret-string "your-secret-key"
   ```

2. **Kubernetes Secrets:**
   ```bash
   kubectl create secret generic analytics-secrets \
     --from-literal=SECRET_KEY=your-secret-key \
     --from-literal=OPENAI_API_KEY=your-openai-key
   ```

3. **HashiCorp Vault:**
   ```bash
   vault kv put secret/analytics \
     SECRET_KEY=your-secret-key \
     OPENAI_API_KEY=your-openai-key
   ```

## Deployment Options

### Option 1: Docker Deployment

#### Build the Docker Image

```bash
docker build -t analytics-platform:1.0.0 .
```

#### Run with Docker Compose

```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  api:
    image: analytics-platform:1.0.0
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - REDIS_URL=${REDIS_URL}
      - SECRET_KEY=${SECRET_KEY}
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    restart: always
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - api
    restart: always
```

```bash
docker-compose -f docker-compose.prod.yml up -d
```

### Option 2: Kubernetes Deployment

#### Using Helm

```bash
# Install the Helm chart
helm upgrade --install analytics ./helm \
  --namespace analytics \
  --create-namespace \
  --set image.tag=1.0.0 \
  --set ingress.enabled=true \
  --set ingress.host=analytics.yourdomain.com \
  --values helm/values-prod.yaml
```

#### Kubernetes Manifests

```yaml
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: analytics-api
  namespace: analytics
spec:
  replicas: 3
  selector:
    matchLabels:
      app: analytics-api
  template:
    metadata:
      labels:
        app: analytics-api
    spec:
      containers:
      - name: api
        image: analytics-platform:1.0.0
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: analytics-secrets
              key: DATABASE_URL
        - name: SECRET_KEY
          valueFrom:
            secretKeyRef:
              name: analytics-secrets
              key: SECRET_KEY
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "2Gi"
            cpu: "2000m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
```

```bash
kubectl apply -f deployment.yaml
```

## Cloud Platform Deployments

### AWS Deployment

#### Using ECS Fargate

1. **Build and push to ECR:**
   ```bash
   aws ecr create-repository --repository-name analytics-platform
   docker tag analytics-platform:1.0.0 <account-id>.dkr.ecr.us-east-1.amazonaws.com/analytics-platform:1.0.0
   docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/analytics-platform:1.0.0
   ```

2. **Create ECS task definition:**
   ```json
   {
     "family": "analytics-api",
     "networkMode": "awsvpc",
     "requiresCompatibilities": ["FARGATE"],
     "cpu": "1024",
     "memory": "2048",
     "containerDefinitions": [
       {
         "name": "api",
         "image": "<account-id>.dkr.ecr.us-east-1.amazonaws.com/analytics-platform:1.0.0",
         "portMappings": [
           {
             "containerPort": 8000,
             "protocol": "tcp"
           }
         ],
         "environment": [
           {"name": "LOG_LEVEL", "value": "INFO"}
         ],
         "secrets": [
           {
             "name": "SECRET_KEY",
             "valueFrom": "arn:aws:secretsmanager:us-east-1:xxx:secret:analytics-secret-key"
           }
         ]
       }
     ]
   }
   ```

#### Using RDS and ElastiCache

```bash
# Create RDS PostgreSQL instance
aws rds create-db-instance \
  --db-instance-identifier analytics-db \
  --db-instance-class db.t3.medium \
  --engine postgres \
  --master-username analytics \
  --master-user-password <password>

# Create ElastiCache Redis cluster
aws elasticache create-cache-cluster \
  --cache-cluster-id analytics-cache \
  --cache-node-type cache.t3.micro \
  --engine redis
```

### Google Cloud Platform

#### Using Cloud Run

```bash
# Build and push to GCR
gcloud builds submit --tag gcr.io/<project-id>/analytics-platform:1.0.0

# Deploy to Cloud Run
gcloud run deploy analytics-api \
  --image gcr.io/<project-id>/analytics-platform:1.0.0 \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars LOG_LEVEL=INFO \
  --set-secrets=SECRET_KEY=analytics-secret:latest
```

### Azure Deployment

#### Using Azure Container Instances

```bash
# Create resource group
az group create --name analytics-rg --location eastus

# Create container instance
az container create \
  --resource-group analytics-rg \
  --name analytics-api \
  --image analytics-platform:1.0.0 \
  --dns-name-label analytics-api \
  --ports 8000 \
  --environment-variables LOG_LEVEL=INFO \
  --secure-environment-variables SECRET_KEY=<value>
```

## Post-Deployment

### 1. Verify Deployment

```bash
# Check health endpoint
curl https://analytics.yourdomain.com/health

# Check readiness
curl https://analytics.yourdomain.com/ready

# View API docs
curl https://analytics.yourdomain.com/docs
```

### 2. Run Database Migrations

```bash
# If using Alembic
docker exec -it analytics-api alembic upgrade head
```

### 3. Configure SSL/TLS

Use Let's Encrypt for free SSL certificates:

```bash
certbot --nginx -d analytics.yourdomain.com
```

### 4. Set Up Monitoring

- Configure Prometheus to scrape `/metrics`
- Set up Grafana dashboards
- Configure alerts in AlertManager
- Enable application logs aggregation (ELK, Datadog, etc.)

## Monitoring and Maintenance

### Health Checks

Regularly monitor:
- `/health` - Basic health check
- `/ready` - Readiness check with dependencies
- `/metrics` - Prometheus metrics

### Metrics to Monitor

- Request rate and latency
- Error rates
- Database connection pool usage
- Cache hit/miss ratio
- ETL job success/failure rate
- AI API usage and costs

### Backup Strategy

1. **Database Backups:**
   ```bash
   # Daily automated backups
   pg_dump -h <db-host> -U <user> analytics > backup-$(date +%Y%m%d).sql
   ```

2. **Configuration Backups:**
   - Store all configuration in version control
   - Back up secrets to secure storage

### Scaling

#### Horizontal Scaling

```bash
# Kubernetes
kubectl scale deployment analytics-api --replicas=5

# ECS
aws ecs update-service \
  --cluster analytics-cluster \
  --service analytics-api \
  --desired-count 5
```

#### Vertical Scaling

Update resource limits in deployment configurations and redeploy.

### Rolling Updates

```bash
# Kubernetes
kubectl set image deployment/analytics-api \
  api=analytics-platform:1.1.0 \
  --record

kubectl rollout status deployment/analytics-api

# Rollback if needed
kubectl rollout undo deployment/analytics-api
```

### Maintenance Windows

Plan for:
- Database maintenance and upgrades
- Security patches
- Dependency updates
- Performance optimization

## Troubleshooting

### Common Issues

1. **Database connection failures:**
   - Check DATABASE_URL configuration
   - Verify network connectivity
   - Check database credentials

2. **High memory usage:**
   - Monitor connection pool sizes
   - Check for memory leaks
   - Adjust worker count

3. **Slow API responses:**
   - Check database query performance
   - Monitor cache hit rates
   - Review API endpoint metrics

### Logs

```bash
# Kubernetes
kubectl logs -f deployment/analytics-api

# Docker
docker logs -f analytics-api

# AWS CloudWatch
aws logs tail /aws/ecs/analytics-api --follow
```

## Security Checklist

- [ ] All secrets stored securely (not in code)
- [ ] HTTPS/TLS enabled
- [ ] Database connections encrypted
- [ ] Security headers configured
- [ ] Rate limiting enabled
- [ ] Input validation implemented
- [ ] CORS properly configured
- [ ] Regular security updates
- [ ] Vulnerability scanning enabled
- [ ] Access logs monitored

## Support

For deployment issues:
- Check the logs first
- Review the troubleshooting guide
- Open an issue on GitHub
- Contact the maintainers

## Resources

- [Docker Documentation](https://docs.docker.com/)
- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [AWS ECS Documentation](https://docs.aws.amazon.com/ecs/)
- [FastAPI Deployment](https://fastapi.tiangolo.com/deployment/)
