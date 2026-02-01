# VPS Deployment Guide – Save Mo Finance API

Guide to deploy the **Save Mo Finance API** (FastAPI backend) on a Linux VPS using the image published to GitHub Container Registry (GHCR).

## Prerequisites

- Linux VPS (Ubuntu/Debian recommended)
- SSH access
- Root or sudo

## Step 1: Connect to the VPS

```bash
ssh root@your-vps-ip
# or
ssh username@your-vps-ip
```

## Step 2: Update system

```bash
# Ubuntu/Debian
sudo apt update && sudo apt upgrade -y

# CentOS/RHEL
sudo yum update -y
```

## Step 3: Install Docker

### Ubuntu/Debian

```bash
sudo apt install -y apt-transport-https ca-certificates curl gnupg lsb-release
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
sudo systemctl start docker && sudo systemctl enable docker
docker --version
```

### CentOS/RHEL

```bash
sudo yum install -y yum-utils
sudo yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
sudo yum install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
sudo systemctl start docker && sudo systemctl enable docker
docker --version
```

## Step 4: Authenticate with GitHub Container Registry

```bash
# Create a PAT: GitHub → Settings → Developer settings → Personal access tokens
# Scope: read:packages

echo YOUR_GITHUB_TOKEN | docker login ghcr.io -u YOUR_GITHUB_USERNAME --password-stdin
```

Replace `YOUR_GITHUB_TOKEN` and `YOUR_GITHUB_USERNAME` with your values.

## Step 5: Deploy the API

The API runs on **port 8000**. Health check: **GET /api/v1/health**.

Use either **API + PostgreSQL (Compose)** or **API only** (external database).

### Option A: API + PostgreSQL (Docker Compose, recommended)

Creates both the API and a Postgres database on the VPS.

```bash
mkdir -p ~/savemo-api
cd ~/savemo-api
```

Create `docker-compose.yml` (replace `YOUR_ORG` with your GitHub org or username, and set a strong `POSTGRES_PASSWORD` and `JWT_SECRET_KEY`):

```yaml
version: "3.9"

services:
  db:
    image: postgres:16-alpine
    container_name: savemo_db
    environment:
      POSTGRES_DB: savemo
      POSTGRES_USER: savemo_user
      POSTGRES_PASSWORD: "4e3w2q11423"
    volumes:
      - savemo_db_data:/var/lib/postgresql/data
    ports:
      - "127.0.0.1:5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U savemo_user -d savemo"]
      interval: 10s
      timeout: 5s
      retries: 5

  api:
    image: ghcr.io/mutesasiratimo/savemo_api:latest
    container_name: savemo_api
    depends_on:
      db:
        condition: service_healthy
    environment:
      DATABASE_URL: postgresql+psycopg2://savemo_user:CHANGE_ME_STRONG_PASSWORD@db:5432/savemo
      JWT_SECRET_KEY: "4e3w2q11423!$@#"
      ENVIRONMENT: production
    ports:
      - "8000:8000"
    restart: unless-stopped
    command: sh -c "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000"

volumes:
  savemo_db_data:
```

Deploy:

```bash
docker compose pull
docker compose up -d
docker compose ps
```

API: **http://your-vps-ip:8000**  
Docs: **http://your-vps-ip:8000/docs**  
Health: **http://your-vps-ip:8000/api/v1/health**

### Option B: API only (external PostgreSQL)

If PostgreSQL is already running (e.g. managed DB), run only the API and pass `DATABASE_URL`:

```bash
docker pull ghcr.io/YOUR_ORG/savemo_api:latest

docker run -d \
  --name savemo_api \
  --restart unless-stopped \
  -p 8000:8000 \
  -e DATABASE_URL="postgresql+psycopg2://user:pass@host:5432/dbname" \
  -e JWT_SECRET_KEY="your-jwt-secret" \
  -e ENVIRONMENT=production \
  ghcr.io/YOUR_ORG/savemo_api:latest
```

Run migrations once (same image, one-off command):

```bash
docker run --rm \
  -e DATABASE_URL="postgresql+psycopg2://user:pass@host:5432/dbname" \
  ghcr.io/YOUR_ORG/savemo_api:latest \
  sh -c "alembic upgrade head"
```

Then start the API container as above (without the migration in the command).

## Environment variables

| Variable | Required | Description |
|----------|----------|-------------|
| `DATABASE_URL` | Yes | PostgreSQL URL, e.g. `postgresql+psycopg2://user:pass@host:5432/savemo` |
| `JWT_SECRET_KEY` | Yes (prod) | Secret for access/refresh tokens; use a long random value in production. |
| `ENVIRONMENT` | No | `development` or `production` (default: development). |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | No | Access token lifetime (default: 1440). |
| `REFRESH_TOKEN_EXPIRE_DAYS` | No | Refresh token lifetime (default: 7). |

## Security: firewall and reverse proxy

### Firewall (UFW, Ubuntu/Debian)

```bash
sudo apt install -y ufw
sudo ufw allow 22/tcp
sudo ufw allow 8000/tcp   # or only 80/443 if using Nginx
sudo ufw enable
sudo ufw status
```

### Nginx reverse proxy (recommended)

```bash
sudo apt install -y nginx
sudo nano /etc/nginx/sites-available/savemo-api
```

Example config (replace `your-domain.com`):

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }
}
```

Enable and test:

```bash
sudo ln -s /etc/nginx/sites-available/savemo-api /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

Then bind the API to localhost only (in compose or `docker run`): `127.0.0.1:8000:8000`.

### SSL with Let's Encrypt

```bash
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

## Verify deployment

```bash
# Health
curl http://localhost:8000/api/v1/health

# With Nginx (replace your-domain.com)
curl http://your-domain.com/api/v1/health
```

Expected: `{"status":"ok"}`

Default admin (if seed migration was run): **admin@email.com** / **admin123**. Change the password in production.

## Updating the API

### Compose (Option A)

```bash
cd ~/savemo-api
docker compose pull
docker compose up -d
docker image prune -af
```

### API-only (Option B)

```bash
docker pull ghcr.io/YOUR_ORG/savemo_api:latest
docker stop savemo_api
docker rm savemo_api
# Run the same docker run command as in Option B above
```

## Monitoring and troubleshooting

```bash
# Logs
docker logs -f savemo_api

# Last 100 lines
docker logs --tail 100 savemo_api

# Compose
docker compose logs -f

# Resource usage
docker stats savemo_api
```

### Container won’t start

- Check logs: `docker logs savemo_api`
- Ensure `DATABASE_URL` is correct and the database is reachable
- Ensure port 8000 is free: `ss -tulpn | grep 8000`

### Can’t pull image

- Re-login: `echo YOUR_TOKEN | docker login ghcr.io -u YOUR_USERNAME --password-stdin`
- Confirm image name matches your repo: `ghcr.io/<owner>/<repo>:latest`

## Quick reference

| Item | Value |
|------|--------|
| API port | 8000 |
| Health | GET /api/v1/health |
| Docs | /docs, /redoc |
| API prefix | /api/v1 |
| Auth | Bearer token (login: POST /api/v1/auth/login or /api/v1/auth/login/json) |

```bash
# Deploy (Compose)
cd ~/savemo-api && docker compose up -d

# Update
docker compose pull && docker compose up -d

# Logs
docker compose logs -f

# Stop
docker compose down
```

Replace `YOUR_ORG` in image names with your GitHub org or username (e.g. `ghcr.io/yourorg/savemo_api:latest`).
