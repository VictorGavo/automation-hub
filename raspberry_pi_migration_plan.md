# Raspberry Pi Migration Plan
## Infrastructure Migration from Cloudflare to Self-Hosted Pi

**Context**: Moving from Cloudflare tunneling to Raspberry Pi self-hosting for better control, learning, and cost optimization.

**Current Architecture**: 
- Flask app running locally with Cloudflare tunnel for external access
- Google Apps Script webhooks point to Cloudflare URLs
- Local PostgreSQL database
- Google Drive sync for file operations

**Target Architecture**:
- Flask app on Raspberry Pi with direct domain access
- Nginx reverse proxy with SSL termination
- PostgreSQL database on Pi
- DNS pointing to Pi's public IP

---

## Phase 1: Pre-Migration Assessment & Planning

### 1.1 Current Dependencies Analysis ✅

**External Webhook Dependencies:**
- Google Apps Script SOD form → `POST /webhook/sod`  
- Google Apps Script EOD form → `POST /webhook/eod`
- Currently using Cloudflare tunnel for external access

**Current Configuration:**
```python
# From config.py
WEBHOOK_SECRET = os.getenv('WEBHOOK_SECRET', None)  # Optional validation
```

**Network Requirements:**
- Inbound HTTPS (443) for webhook access
- Outbound HTTPS for Notion API, Google Drive API
- PostgreSQL local access (5432)

### 1.2 Domain & DNS Requirements

**Needed:**
- Domain name (your website domain)
- DNS A record pointing to Pi's public IP
- Dynamic DNS if IP changes (optional)

**SSL Certificate:**
- Let's Encrypt via certbot for free SSL
- Auto-renewal setup required

### 1.3 Raspberry Pi Specifications

**Minimum Requirements:**
- Raspberry Pi 4B (4GB+ RAM recommended)  
- 32GB+ microSD card (Class 10)
- Reliable power supply
- Ethernet connection (recommended over WiFi for stability)

---

## Phase 2: Raspberry Pi Environment Setup

### 2.1 Operating System & Base Setup

```bash
# Install Raspberry Pi OS Lite (server)
# Enable SSH during initial setup
sudo apt update && sudo apt upgrade -y

# Install essential packages
sudo apt install -y python3 python3-pip python3-venv postgresql nginx certbot python3-certbot-nginx git
```

### 2.2 Database Migration

**PostgreSQL Setup:**
```bash
# Install and configure PostgreSQL on Pi
sudo postgresql-setup --initdb  # If needed
sudo systemctl enable postgresql
sudo systemctl start postgresql

# Create database and user
sudo -u postgres createuser -P automation_user
sudo -u postgres createdb -O automation_user automation_hub

# Export from current database
pg_dump -h localhost -U admin automation_hub > automation_hub_backup.sql

# Import to Pi database  
psql -h pi_ip -U automation_user -d automation_hub < automation_hub_backup.sql
```

### 2.3 Application Deployment

**Python Environment:**
```bash
# Create application directory
sudo mkdir -p /opt/automation-hub
sudo chown pi:pi /opt/automation-hub
cd /opt/automation-hub

# Clone repository
git clone https://github.com/VictorGavo/automation-hub.git .
git checkout main  # Use stable branch

# Setup virtual environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**Environment Configuration:**
```bash
# Create production .env file
cat > .env << EOF
# Database
DB_HOST=localhost
DB_USER=automation_user
DB_PASSWORD=your_secure_password
DB_NAME=automation_hub

# Flask
SECRET_KEY=your_super_secret_key_here
DEBUG=False

# APIs
NOTION_API_TOKEN=your_notion_token
NOTION_ENABLED=true
GOOGLE_DRIVE_ENABLED=true

# Production settings
WEBHOOK_SECRET=your_webhook_secret
TIMEZONE=America/Los_Angeles
EOF
```

---

## Phase 3: Reverse Proxy & SSL Setup

### 3.1 Nginx Configuration

**Main Configuration:**
```nginx
# /etc/nginx/sites-available/automation-hub
server {
    listen 80;
    server_name yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com;
    
    # SSL Configuration (Let's Encrypt)
    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
    
    # Security headers
    add_header X-Content-Type-Options nosniff;
    add_header X-Frame-Options DENY;
    add_header X-XSS-Protection "1; mode=block";
    
    # Rate limiting
    limit_req_zone $binary_remote_addr zone=webhook:10m rate=10r/m;
    
    # Webhook endpoints with rate limiting  
    location /webhook/ {
        limit_req zone=webhook burst=5;
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Webhook-specific settings
        client_max_body_size 1M;
        proxy_read_timeout 30s;
    }
    
    # Health check endpoint
    location /health {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
    }
    
    # Block other endpoints for security
    location / {
        return 404;
    }
}
```

**Enable Configuration:**
```bash
sudo ln -s /etc/nginx/sites-available/automation-hub /etc/nginx/sites-enabled/
sudo nginx -t  # Test configuration
```

### 3.2 SSL Certificate Setup

```bash
# Obtain SSL certificate
sudo certbot --nginx -d yourdomain.com

# Test auto-renewal
sudo certbot renew --dry-run

# Setup auto-renewal cron job
echo "0 12 * * * /usr/bin/certbot renew --quiet" | sudo tee -a /etc/crontab
```

---

## Phase 4: Service Management & Monitoring

### 4.1 Systemd Service Setup

**Flask Application Service:**
```ini
# /etc/systemd/system/automation-hub.service
[Unit]
Description=Automation Hub Flask Application
After=network.target postgresql.service

[Service]
Type=simple
User=pi
Group=pi
WorkingDirectory=/opt/automation-hub
Environment=PATH=/opt/automation-hub/venv/bin
ExecStart=/opt/automation-hub/venv/bin/python app.py
Restart=always
RestartSec=10

# Security settings
NoNewPrivileges=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=/opt/automation-hub

[Install]
WantedBy=multi-user.target
```

**Enable and Start:**
```bash
sudo systemctl daemon-reload
sudo systemctl enable automation-hub
sudo systemctl start automation-hub
sudo systemctl status automation-hub
```

### 4.2 Monitoring & Logging

**Log Management:**
```bash
# Setup log rotation
sudo tee /etc/logrotate.d/automation-hub << EOF
/opt/automation-hub/automation_hub.log {
    daily
    missingok
    rotate 7
    compress
    notifempty
    create 644 pi pi
}
EOF
```

**Health Monitoring Script:**
```bash
#!/bin/bash
# /opt/automation-hub/health_check.sh
curl -f http://localhost:5000/health || systemctl restart automation-hub
```

---

## Phase 5: Network & Security Configuration

### 5.1 Router Port Forwarding

**Required Port Forwards:**
- External Port 443 → Pi IP:443 (HTTPS)
- External Port 80 → Pi IP:80 (HTTP redirect)

### 5.2 Firewall Configuration

```bash
# Enable UFW firewall
sudo ufw enable

# Allow SSH (be careful!)
sudo ufw allow ssh

# Allow HTTP/HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Deny all other incoming
sudo ufw default deny incoming
sudo ufw default allow outgoing

# Check status
sudo ufw status verbose
```

### 5.3 Security Hardening

**SSH Security:**
```bash
# Disable password authentication (use keys only)
sudo sed -i 's/#PasswordAuthentication yes/PasswordAuthentication no/' /etc/ssh/sshd_config
sudo systemctl restart ssh
```

**Fail2Ban Protection:**
```bash
sudo apt install fail2ban

# Configure fail2ban for nginx
sudo tee /etc/fail2ban/jail.local << EOF
[nginx-limit-req]
enabled = true
filter = nginx-limit-req
action = iptables-multiport[name=ReqLimit, port="http,https", protocol=tcp]
logpath = /var/log/nginx/error.log
findtime = 600
bantime = 7200
maxretry = 10
EOF

sudo systemctl restart fail2ban
```

---

## Phase 6: Migration Execution

### 6.1 Pre-Migration Testing

**Local Testing:**
```bash
# Test all endpoints locally
python test_enhanced_processing.py
python test_full_integration.py

# Test database connectivity
python -c "from database import DatabaseManager; db = DatabaseManager(); print('DB OK')"
```

### 6.2 DNS Cutover Process

**Step-by-Step Migration:**

1. **Prepare Pi Environment** (Complete Phases 1-5)
2. **Final Database Sync** 
   ```bash
   # Export latest data
   pg_dump automation_hub > final_backup.sql
   # Import to Pi
   psql -h pi_ip -U automation_user -d automation_hub < final_backup.sql
   ```

3. **Update DNS Records**
   ```
   A Record: yourdomain.com → Pi_Public_IP
   TTL: 300 (5 minutes for quick rollback)
   ```

4. **Update Google Apps Script URLs**
   ```javascript
   // Change from Cloudflare URLs to:
   const SOD_WEBHOOK = 'https://yourdomain.com/webhook/sod';
   const EOD_WEBHOOK = 'https://yourdomain.com/webhook/eod';
   ```

5. **Monitor & Validate**
   ```bash
   # Monitor nginx logs
   sudo tail -f /var/log/nginx/access.log
   
   # Check application logs
   sudo journalctl -u automation-hub -f
   
   # Test webhooks
   curl -X POST https://yourdomain.com/health
   ```

### 6.3 Rollback Plan

**If Issues Occur:**
1. Revert DNS to Cloudflare IPs (TTL allows quick change)
2. Revert Google Apps Script URLs
3. Debug Pi issues while Cloudflare handles traffic

---

## Phase 7: Post-Migration Optimization

### 7.1 Performance Tuning

**Database Optimization:**
```sql
-- Analyze database performance
ANALYZE;
-- Add indexes for common queries
CREATE INDEX IF NOT EXISTS idx_daily_entries_date ON daily_entries(date);
```

**Nginx Caching:**
```nginx
# Add to nginx config for static content
location ~* \.(css|js|png|jpg|jpeg|gif|ico|svg)$ {
    expires 1y;
    add_header Cache-Control "public, immutable";
}
```

### 7.2 Backup Strategy

**Automated Backups:**
```bash
#!/bin/bash
# /opt/automation-hub/backup.sh
DATE=$(date +%Y%m%d_%H%M%S)
pg_dump automation_hub > /opt/backups/automation_hub_$DATE.sql
find /opt/backups -name "automation_hub_*.sql" -mtime +7 -delete

# Add to crontab
# 0 2 * * * /opt/automation-hub/backup.sh
```

### 7.3 Monitoring Dashboard

**Simple Health Dashboard:**
```python
# Add to app.py
@app.route('/status')
def system_status():
    return jsonify({
        'database': 'healthy',
        'disk_usage': psutil.disk_usage('/').percent,
        'memory_usage': psutil.virtual_memory().percent,
        'uptime': 'system_uptime'
    })
```

---

## Implementation Timeline

**Week 1: Preparation**
- [ ] Acquire domain/setup DNS provider
- [ ] Order Raspberry Pi if needed
- [ ] Document current Cloudflare configuration

**Week 2: Pi Setup**  
- [ ] Install OS and base packages
- [ ] Configure PostgreSQL and migrate data
- [ ] Deploy application code

**Week 3: Network & Security**
- [ ] Configure nginx and SSL
- [ ] Setup firewall and security hardening
- [ ] Configure router port forwarding

**Week 4: Testing & Migration**
- [ ] Comprehensive testing of Pi environment
- [ ] DNS cutover during low-usage period
- [ ] Update Google Apps Script webhooks
- [ ] Monitor and validate functionality

**Ongoing: Maintenance**
- [ ] Weekly backup verification
- [ ] Monthly security updates
- [ ] Quarterly performance review

---

## Benefits of Migration

**Control & Learning:**
- Full control over infrastructure
- Learn nginx, SSL, system administration
- Better debugging and logging capabilities

**Cost & Performance:**
- No Cloudflare tunnel dependency
- Reduced latency for database operations
- One-time Pi cost vs ongoing service fees

**Reliability:**
- Direct connection eliminates tunnel failures
- Local database reduces network dependencies
- Simplified architecture reduces failure points

---

## Risk Mitigation

**High Priority Risks:**
1. **Power/Internet Outage**: UPS for Pi, mobile hotspot backup
2. **Hardware Failure**: Regular backups, spare Pi ready
3. **Security Breach**: Fail2ban, regular updates, monitoring
4. **DNS Issues**: Keep Cloudflare as backup option

**Medium Priority Risks:**
1. **Performance Issues**: Monitor resources, scale if needed
2. **SSL Expiration**: Automated renewal monitoring
3. **Database Corruption**: Daily backups, transaction logs

This migration plan provides a comprehensive roadmap for moving from Cloudflare tunneling to a self-hosted Raspberry Pi solution while maintaining reliability and security.
