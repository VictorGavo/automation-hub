#!/bin/bash
# Raspberry Pi Automation Hub Setup Script
# Run this on a fresh Raspberry Pi OS installation

set -e  # Exit on any error

echo "🚀 Automation Hub - Raspberry Pi Setup"
echo "======================================"

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration variables
APP_DIR="/opt/automation-hub"
APP_USER="pi"
DB_NAME="automation_hub"
DB_USER="automation_user"

print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_root() {
    if [ "$EUID" -eq 0 ]; then
        print_error "Don't run this script as root. Run as pi user with sudo privileges."
        exit 1
    fi
}

update_system() {
    print_status "Updating system packages..."
    sudo apt update && sudo apt upgrade -y
}

install_packages() {
    print_status "Installing required packages..."
    sudo apt install -y \
        python3 \
        python3-pip \
        python3-venv \
        postgresql \
        postgresql-contrib \
        nginx \
        certbot \
        python3-certbot-nginx \
        git \
        curl \
        fail2ban \
        ufw \
        psmisc
}

setup_postgresql() {
    print_status "Setting up PostgreSQL..."
    
    # Start and enable PostgreSQL
    sudo systemctl enable postgresql
    sudo systemctl start postgresql
    
    # Create database user
    print_status "Creating database user: $DB_USER"
    sudo -u postgres createuser -P $DB_USER || true
    
    # Create database
    print_status "Creating database: $DB_NAME"
    sudo -u postgres createdb -O $DB_USER $DB_NAME || true
    
    print_status "PostgreSQL setup complete"
}

setup_application() {
    print_status "Setting up application directory..."
    
    # Create application directory
    sudo mkdir -p $APP_DIR
    sudo chown $APP_USER:$APP_USER $APP_DIR
    
    # Clone repository (assuming it's already on the Pi or will be copied)
    if [ ! -d "$APP_DIR/.git" ]; then
        print_warning "Application code not found. Please clone the repository to $APP_DIR"
        print_warning "Run: git clone https://github.com/VictorGavo/automation-hub.git $APP_DIR"
        return
    fi
    
    cd $APP_DIR
    
    # Setup Python virtual environment
    print_status "Creating Python virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
    
    # Install Python dependencies
    print_status "Installing Python dependencies..."
    pip install --upgrade pip
    pip install -r requirements.txt
}

setup_environment_file() {
    print_status "Setting up environment configuration..."
    
    if [ ! -f "$APP_DIR/.env" ]; then
        cat > $APP_DIR/.env << EOF
# Database Configuration
DB_HOST=localhost
DB_USER=$DB_USER
DB_PASSWORD=CHANGE_ME_NOW
DB_NAME=$DB_NAME

# Flask Configuration
SECRET_KEY=CHANGE_ME_TO_RANDOM_STRING
DEBUG=False

# API Configuration
NOTION_API_TOKEN=
NOTION_DAILY_CAPTURE_PAGE_ID=
NOTION_ENABLED=false

# Google Drive Configuration
GOOGLE_DRIVE_ENABLED=false
GOOGLE_DRIVE_SYNC_PATH=/opt/automation-hub/daily_notes

# Obsidian Integration
OBSIDIAN_GOALS_ENABLED=false

# Security
WEBHOOK_SECRET=CHANGE_ME_TO_RANDOM_STRING

# Timezone
TIMEZONE=America/Los_Angeles
EOF
        
        print_warning "Created .env file at $APP_DIR/.env"
        print_warning "IMPORTANT: Edit this file with your actual configuration values!"
        print_warning "Don't forget to set secure passwords and API tokens!"
    else
        print_status ".env file already exists, skipping creation"
    fi
}

setup_systemd_service() {
    print_status "Setting up systemd service..."
    
    sudo tee /etc/systemd/system/automation-hub.service > /dev/null << EOF
[Unit]
Description=Automation Hub Flask Application
After=network.target postgresql.service

[Service]
Type=simple
User=$APP_USER
Group=$APP_USER
WorkingDirectory=$APP_DIR
Environment=PATH=$APP_DIR/venv/bin
ExecStart=$APP_DIR/venv/bin/python app.py
Restart=always
RestartSec=10

# Security settings
NoNewPrivileges=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=$APP_DIR

[Install]
WantedBy=multi-user.target
EOF

    # Reload systemd and enable service
    sudo systemctl daemon-reload
    sudo systemctl enable automation-hub
    
    print_status "Systemd service created and enabled"
    print_warning "Service will start automatically on boot"
    print_warning "Start manually with: sudo systemctl start automation-hub"
}

setup_nginx() {
    print_status "Setting up Nginx configuration..."
    
    # Remove default site
    sudo rm -f /etc/nginx/sites-enabled/default
    
    # Create automation-hub site configuration
    sudo tee /etc/nginx/sites-available/automation-hub > /dev/null << 'EOF'
server {
    listen 80;
    server_name _;  # Will be replaced with actual domain
    
    location / {
        return 301 https://$server_name$request_uri;
    }
}

server {
    listen 443 ssl http2 default_server;
    server_name _;  # Will be replaced with actual domain
    
    # SSL Configuration (placeholder - will be configured by certbot)
    ssl_certificate /etc/ssl/certs/ssl-cert-snakeoil.pem;
    ssl_certificate_key /etc/ssl/private/ssl-cert-snakeoil.key;
    
    # Security headers
    add_header X-Content-Type-Options nosniff;
    add_header X-Frame-Options DENY;
    add_header X-XSS-Protection "1; mode=block";
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    
    # Rate limiting zones
    limit_req_zone $binary_remote_addr zone=webhook:10m rate=10r/m;
    limit_req_zone $binary_remote_addr zone=api:10m rate=30r/m;
    
    # Webhook endpoints with rate limiting
    location /webhook/ {
        limit_req zone=webhook burst=5 nodelay;
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Webhook-specific settings
        client_max_body_size 1M;
        proxy_read_timeout 30s;
        proxy_connect_timeout 10s;
    }
    
    # Health check endpoint
    location /health {
        limit_req zone=api burst=10 nodelay;
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    # API endpoints
    location /api/ {
        limit_req zone=api burst=20 nodelay;
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # Block all other endpoints for security
    location / {
        return 404;
    }
}
EOF

    # Enable the site
    sudo ln -sf /etc/nginx/sites-available/automation-hub /etc/nginx/sites-enabled/
    
    # Test nginx configuration
    if sudo nginx -t; then
        print_status "Nginx configuration is valid"
        sudo systemctl enable nginx
        sudo systemctl restart nginx
    else
        print_error "Nginx configuration test failed!"
        exit 1
    fi
}

setup_firewall() {
    print_status "Setting up UFW firewall..."
    
    # Reset UFW to defaults
    sudo ufw --force reset
    
    # Set default policies
    sudo ufw default deny incoming
    sudo ufw default allow outgoing
    
    # Allow SSH (be careful!)
    sudo ufw allow ssh
    
    # Allow HTTP and HTTPS
    sudo ufw allow 80/tcp
    sudo ufw allow 443/tcp
    
    # Enable firewall
    sudo ufw --force enable
    
    print_status "Firewall configured and enabled"
    sudo ufw status verbose
}

setup_fail2ban() {
    print_status "Setting up Fail2Ban..."
    
    # Create local jail configuration
    sudo tee /etc/fail2ban/jail.local > /dev/null << 'EOF'
[DEFAULT]
bantime = 1h
findtime = 10m
maxretry = 5

[sshd]
enabled = true

[nginx-http-auth]
enabled = true

[nginx-limit-req]
enabled = true
filter = nginx-limit-req
action = iptables-multiport[name=ReqLimit, port="http,https", protocol=tcp]
logpath = /var/log/nginx/error.log
findtime = 600
bantime = 7200
maxretry = 10
EOF

    # Start and enable fail2ban
    sudo systemctl enable fail2ban
    sudo systemctl restart fail2ban
    
    print_status "Fail2Ban configured and started"
}

create_backup_script() {
    print_status "Creating backup script..."
    
    sudo mkdir -p /opt/backups
    sudo chown $APP_USER:$APP_USER /opt/backups
    
    tee $APP_DIR/backup.sh > /dev/null << EOF
#!/bin/bash
# Automated backup script for Automation Hub

DATE=\$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/opt/backups"
DB_NAME="$DB_NAME"
DB_USER="$DB_USER"

# Create database backup
pg_dump -h localhost -U \$DB_USER \$DB_NAME > \$BACKUP_DIR/automation_hub_\$DATE.sql

# Create application backup (excluding venv and cache)
tar --exclude='venv' --exclude='__pycache__' --exclude='*.pyc' \\
    -czf \$BACKUP_DIR/app_backup_\$DATE.tar.gz -C $APP_DIR .

# Remove backups older than 7 days
find \$BACKUP_DIR -name "automation_hub_*.sql" -mtime +7 -delete
find \$BACKUP_DIR -name "app_backup_*.tar.gz" -mtime +7 -delete

echo "Backup completed: \$DATE"
EOF

    chmod +x $APP_DIR/backup.sh
    
    # Add to crontab for daily backups at 2 AM
    (crontab -u $APP_USER -l 2>/dev/null; echo "0 2 * * * $APP_DIR/backup.sh >> /var/log/automation-hub-backup.log 2>&1") | crontab -u $APP_USER -
    
    print_status "Backup script created and scheduled"
}

create_health_check_script() {
    print_status "Creating health check script..."
    
    tee $APP_DIR/health_check.sh > /dev/null << 'EOF'
#!/bin/bash
# Health check script for Automation Hub

LOG_FILE="/var/log/automation-hub-health.log"

# Check if application is responding
if curl -f -s http://localhost:5000/health > /dev/null; then
    echo "$(date): Health check passed" >> $LOG_FILE
else
    echo "$(date): Health check failed - restarting service" >> $LOG_FILE
    sudo systemctl restart automation-hub
    
    # Wait a bit and check again
    sleep 10
    if curl -f -s http://localhost:5000/health > /dev/null; then
        echo "$(date): Service restart successful" >> $LOG_FILE
    else 
        echo "$(date): Service restart failed - manual intervention required" >> $LOG_FILE
    fi
fi
EOF

    chmod +x $APP_DIR/health_check.sh
    
    # Add to crontab for every 5 minutes
    (crontab -u $APP_USER -l 2>/dev/null; echo "*/5 * * * * $APP_DIR/health_check.sh") | crontab -u $APP_USER -
    
    print_status "Health check script created and scheduled"
}

print_completion_summary() {
    echo ""
    echo "🎉 Raspberry Pi Setup Complete!"
    echo "==============================="
    echo ""
    echo "Next steps:"
    echo "1. Edit $APP_DIR/.env with your configuration"
    echo "2. Update your domain's DNS to point to this Pi's IP"
    echo "3. Run: sudo certbot --nginx -d yourdomain.com"
    echo "4. Start the service: sudo systemctl start automation-hub"
    echo "5. Update Google Apps Script webhook URLs"
    echo ""
    echo "Useful commands:"
    echo "- Check service status: sudo systemctl status automation-hub"
    echo "- View logs: sudo journalctl -u automation-hub -f"
    echo "- Test health: curl http://localhost:5000/health"
    echo "- Nginx config test: sudo nginx -t"
    echo ""
    echo "Configuration files:"
    echo "- Application: $APP_DIR/.env"
    echo "- Nginx: /etc/nginx/sites-available/automation-hub"
    echo "- Service: /etc/systemd/system/automation-hub.service"
    echo ""
    print_warning "Don't forget to secure your .env file with proper passwords!"
}

# Main execution
main() {
    check_root
    update_system
    install_packages
    setup_postgresql
    setup_application
    setup_environment_file
    setup_systemd_service
    setup_nginx
    setup_firewall
    setup_fail2ban
    create_backup_script
    create_health_check_script
    print_completion_summary
}

# Run main function
main "$@"
