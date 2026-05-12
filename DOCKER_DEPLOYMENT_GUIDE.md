# Docker Deployment Guide

## Overview

This guide covers containerization and deployment of the Banking Support AI Agent Chatbot using Docker and Docker Compose.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Nginx Reverse Proxy (Port 80/443)       │
│                    (Optional - Production Only)             │
└──────────┬─────────────────────────────┬──────────────────┘
           │                             │
           ▼                             ▼
┌─────────────────────────┐    ┌──────────────────────────┐
│   Streamlit (8501)      │    │   FastAPI (8000)         │
│   - UI Layer            │    │   - Services Layer       │
│   - Chat Interface      │    │   - Agent Routing        │
│   - Real-time Updates   │    │   - RAG Orchestration    │
└────────────┬────────────┘    └──────────┬───────────────┘
             │                            │
             └────────────┬───────────────┘
                          │
                    ┌─────▼──────┐
                    │  Weaviate  │
                    │  Database  │
                    └────────────┘
```

## Prerequisites

- Docker (v20.10+)
- Docker Compose (v2.0+)
- 4GB+ available RAM
- 10GB+ disk space

## Quick Start

### 1. Development Deployment (All-in-One)

```bash
# Clone/navigate to project directory
cd path/to/Support_Resolution_Multi_Agent_AG_Chatbot

# Build and start all services
docker-compose up --build

# Output will show:
# - Weaviate: http://localhost:8080
# - FastAPI: http://localhost:8000
# - Streamlit: http://localhost:8501
```

**First Run**: Services may take 1-2 minutes to fully initialize.

### 2. Production Deployment (with Nginx)

```bash
# Start with production profile (includes Nginx)
docker-compose --profile prod up -d --build

# Services accessible at:
# - http://localhost (Nginx reverse proxy)
# - http://localhost/docs (FastAPI docs)
# - http://localhost:8501 (Direct Streamlit access)
```

## Individual Service Deployment

### Start Only FastAPI

```bash
docker-compose up -d fastapi weaviate
# Access at: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

### Start Only Streamlit

```bash
docker-compose up -d streamlit fastapi weaviate
# Access at: http://localhost:8501
```

### Start Only Weaviate

```bash
docker-compose up -d weaviate
# Access at: http://localhost:8080
```

## Configuration

### 1. Environment Variables

```bash
# Copy example env file
cp .env.example .env

# Edit with your configuration
nano .env
```

**Key Variables:**
- `FASTAPI_HOST`: FastAPI server host (default: 0.0.0.0)
- `FASTAPI_PORT`: FastAPI server port (default: 8000)
- `STREAMLIT_PORT`: Streamlit port (default: 8501)
- `WEAVIATE_URL`: Weaviate database URL
- `LLM_API_KEY`: Your LLM provider API key
- `LOG_LEVEL`: Logging level (debug/info/warning)

### 2. Docker Compose Override

Create `docker-compose.override.yml` for local development:

```yaml
version: '3.8'
services:
  fastapi:
    ports:
      - "8000:8000"
    environment:
      - DEBUG=true
  streamlit:
    ports:
      - "8501:8501"
```

## Common Commands

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f fastapi
docker-compose logs -f streamlit
docker-compose logs -f weaviate

# Last 100 lines
docker-compose logs --tail=100
```

### Service Management

```bash
# Stop all services
docker-compose stop

# Stop specific service
docker-compose stop fastapi

# Restart services
docker-compose restart

# Remove all containers and volumes
docker-compose down -v

# Rebuild images
docker-compose up -d --build

# Pull latest images
docker-compose pull
```

### Access Services

```bash
# Enter FastAPI container shell
docker-compose exec fastapi /bin/bash

# Enter Streamlit container shell
docker-compose exec streamlit /bin/bash

# Run test in container
docker-compose exec fastapi python -m pytest

# Check container status
docker-compose ps
```

## Health Checks

### Check Service Health

```bash
# FastAPI health
curl http://localhost:8000/docs

# Streamlit health
curl http://localhost:8501

# Weaviate health
curl http://localhost:8080/v1/.well-known/ready
```

### View Health Status in Docker

```bash
# Check running containers
docker ps

# Inspect container health
docker inspect banking_fastapi | grep -A 5 "Health"
```

## Performance Optimization

### Memory Configuration

Edit `docker-compose.yml`:

```yaml
services:
  fastapi:
    deploy:
      resources:
        limits:
          memory: 2G
        reservations:
          memory: 1G
```

### CPU Configuration

```yaml
fastapi:
  deploy:
    resources:
      limits:
        cpus: '1.5'
```

## Volumes and Data Persistence

### Default Volumes

```
weaviate_data/      - Weaviate vector database
logs/               - Application logs
data/               - Feedback and documents
```

### Backup Data

```bash
# Backup volumes
docker run --rm \
  -v chatbot_weaviate_data:/data \
  -v $(pwd)/backup:/backup \
  alpine tar czf /backup/weaviate-backup.tar.gz -C /data .

# Restore volumes
docker run --rm \
  -v chatbot_weaviate_data:/data \
  -v $(pwd)/backup:/backup \
  alpine tar xzf /backup/weaviate-backup.tar.gz -C /data
```

## Production Deployment

### 1. Pre-Production Checklist

- [ ] Set `DEBUG=false` in .env
- [ ] Generate secure `SECRET_KEY`
- [ ] Configure `ALLOWED_HOSTS`
- [ ] Set up SSL certificates
- [ ] Configure email settings
- [ ] Set resource limits
- [ ] Enable logging to persistent volume

### 2. SSL/TLS Configuration

```bash
# Generate self-signed certificate
openssl req -x509 -newkey rsa:4096 -keyout ssl/key.pem -out ssl/cert.pem -days 365 -nodes

# Or use Let's Encrypt with Certbot
certbot certonly --standalone -d your_domain.com
```

### 3. Nginx Configuration for HTTPS

Uncomment HTTPS sections in `nginx.conf` and update domain/certificates.

### 4. Database Backup Strategy

```bash
# Automated daily backup
0 2 * * * docker-compose exec weaviate \
  tar czf /backup/weaviate-$(date +\%Y\%m\%d).tar.gz /var/lib/weaviate
```

### 5. Monitoring and Logging

```bash
# Send logs to external service
docker-compose logs -f | tee >(grep -i error >> /var/log/chatbot-errors.log)

# Monitor resource usage
docker stats
```

## Troubleshooting

### Container Won't Start

```bash
# Check logs
docker-compose logs fastapi

# Verify image exists
docker images | grep banking

# Rebuild image
docker-compose build --no-cache
```

### Port Already in Use

```bash
# Find process using port
lsof -i :8000
lsof -i :8501

# Kill process or use different port
docker-compose down
# Edit docker-compose.yml ports
docker-compose up -d
```

### Weaviate Connection Issues

```bash
# Check Weaviate status
curl http://localhost:8080/v1/.well-known/ready

# Restart Weaviate
docker-compose restart weaviate

# Check network
docker network ls
docker network inspect chatbot_network
```

### Out of Memory

```bash
# Check memory usage
docker stats

# Stop unused containers
docker-compose down

# Increase Docker memory allocation in Docker settings
# For Linux, edit /etc/docker/daemon.json
```

### Streamlit Not Responsive

```bash
# Check Streamlit logs
docker-compose logs -f streamlit

# Restart service
docker-compose restart streamlit

# Clear Streamlit cache
docker-compose exec streamlit rm -rf ~/.streamlit
```

## Scaling

### Horizontal Scaling

For production, consider:

```yaml
version: '3.8'
services:
  fastapi:
    deploy:
      replicas: 3
```

Use with orchestration tools (Kubernetes, Swarm).

### Load Balancing

Use Nginx or AWS ELB to distribute traffic across multiple FastAPI instances.

## Security Best Practices

1. **Never commit .env files** - Use .env.example only
2. **Use secrets management** - Docker Secrets or external vaults
3. **Regular updates** - Keep base images updated
4. **Network isolation** - Use internal networks
5. **Resource limits** - Set CPU/memory constraints
6. **Logging** - Monitor and log all access
7. **HTTPS only** - Use SSL/TLS in production

## Cleanup

### Remove Everything

```bash
# Stop and remove all containers, networks, and volumes
docker-compose down -v

# Remove images
docker rmi banking-chatbot_fastapi banking-chatbot_streamlit

# Clean up Docker system
docker system prune -a --volumes
```

## Support

For issues:
1. Check logs: `docker-compose logs`
2. Verify .env configuration
3. Ensure ports are available
4. Check Docker resources

## References

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [FastAPI Deployment](https://fastapi.tiangolo.com/deployment/docker/)
- [Streamlit Deployment](https://docs.streamlit.io/knowledge-base/tutorials/deploy)
