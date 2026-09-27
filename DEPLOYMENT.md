# Apex Dental Care - Production Deployment & Operations Guide

## 1. Production Topology

```mermaid
graph TD
    Internet((Public Internet))
    LB["HTTPS Reverse Proxy (Nginx / Cloudflare)"]
    Frontend["React Static Assets (Nginx Alpine)"]
    Backend["FastAPI ASGI Application (Gunicorn + Uvicorn)"]
    Database[("MySQL 8.0 Enterprise Cluster")]
    Storage[("Encrypted S3 / Block Storage")]

    Internet -->|TLS 1.3 / Port 443| LB
    LB -->|HTTP Static Assets| Frontend
    LB -->|Reverse Proxy /api/v1| Backend
    Backend -->|TCP Port 3306 Private Network| Database
    Backend -->|Private VPC| Storage
```

---

## 2. Server Requirements & Prerequisites

- **Compute:** Minimum 2 vCPU, 4GB RAM (8GB recommended for ReportLab PDF caching & high concurrent traffic).
- **OS:** Ubuntu 22.04 LTS or Debian 12.
- **Runtime:** Docker Engine 24+ & Docker Compose v2.20+.
- **Storage:** Minimum 50GB NVMe SSD for database and radiological attachments.

---

## 3. Deployment Steps

### Step 1: Clone Repository & Create Environment Configuration
```bash
git clone https://github.com/apex-dental/clinic-system.git /var/www/apex-dental
cd /var/www/apex-dental

cp .env.example .env
# Edit .env with production credentials:
nano .env
```

Ensure the following variables are configured with high-entropy cryptographic strings:
```ini
ENVIRONMENT=production
DEBUG=false
DATABASE_URL=mysql+mysqldb://dental_prod:STRONG_DB_PASS@mysql:3306/dental_clinic
JWT_SECRET=GENERATE_RANDOM_64_CHARACTERS_STRING
JWT_REFRESH_SECRET=GENERATE_ANOTHER_RANDOM_64_CHARACTERS_STRING
CORS_ORIGINS=https://clinic.yourdomain.com
```

### Step 2: Build and Launch Containers
```bash
docker compose -f docker-compose.yml up --build -d
```

### Step 3: Verify Container Health
```bash
# Check container status
docker compose ps

# Check API readiness probe
curl -f http://localhost:8000/api/v1/health/ready
```

---

## 4. HTTPS & SSL / TLS Configuration

For production domain deployment, place Nginx or Caddy in front of the application:

```nginx
# /etc/nginx/sites-available/clinic.yourdomain.com
server {
    listen 80;
    server_name clinic.yourdomain.com;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl http2;
    server_name clinic.yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/clinic.yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/clinic.yourdomain.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    # Security Headers
    add_header Strict-Transport-Security "max-age=63072000; includeSubDomains; preload" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-Frame-Options "DENY" always;

    # Reverse proxy to Docker container
    location / {
        proxy_pass http://127.0.0.1:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto https;
    }
}
```

---

## 5. Database Backup & Disaster Recovery

### Automated Backup Script (`scripts/backup_db.sh`)
```bash
#!/bin/bash
BACKUP_DIR="/var/backups/apex_dental"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
FILENAME="dental_clinic_backup_${TIMESTAMP}.sql.gz"

mkdir -p $BACKUP_DIR

# Perform transactional dump with zero downtime
docker exec apex_dental_mysql mysqldump \
    -u root -prootpassword \
    --single-transaction \
    --quick \
    --routines \
    --triggers \
    dental_clinic | gzip > "${BACKUP_DIR}/${FILENAME}"

# Retain backups for 30 days
find $BACKUP_DIR -name "dental_clinic_backup_*.sql.gz" -mtime +30 -exec rm {} \;

echo "Backup completed: ${BACKUP_DIR}/${FILENAME}"
```

### Scheduled Cron Execution
```cron
# Daily backup at 2:00 AM
0 2 * * * /var/www/apex-dental/scripts/backup_db.sh >> /var/log/dental_backup.log 2>&1
```

### Database Restoration Procedure
```bash
# 1. Decompress backup file
gunzip < /var/backups/apex_dental/dental_clinic_backup_20260927_020000.sql.gz > restore.sql

# 2. Import into MySQL container
docker exec -i apex_dental_mysql mysql -u root -prootpassword dental_clinic < restore.sql

# 3. Re-run migrations to ensure schema consistency
docker exec apex_dental_backend alembic upgrade head
```

---

## 6. Monitoring & Health Probes

- **Liveness Probe:** `GET /api/v1/health` (Returns HTTP 200 if FastAPI process is responsive).
- **Readiness Probe:** `GET /api/v1/health/ready` (Executes `SELECT 1` on active DB connection pool).
- **Application Logs:** Structured JSON logs streamed to standard output, collected via Docker log driver or vector agent.
